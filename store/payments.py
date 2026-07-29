"""Paiements mobile money : Wave et Orange Money (intégrations réelles).

Aucune simulation : les fonctions appellent les vraies API des opérateurs. Les
identifiants marchands sont lus dans les variables d'environnement ; sans eux,
une erreur PaymentNotConfigured est levée (aucun faux paiement n'est validé).

Wave       : https://docs.wave.com/checkout
Orange Money: https://developer.orange.com/apis/om-webpay

Variables d'environnement
  DRESSIT_SITE_URL              URL publique du site (https://…) pour les retours
  WAVE_API_KEY                  clé API Wave (wave_sn_...)
  WAVE_WEBHOOK_SECRET           secret de signature des webhooks Wave
  OM_MERCHANT_KEY               clé marchand Orange Money
  OM_CONSUMER_KEY/OM_CONSUMER_SECRET  identifiants OAuth Orange (ou OM_AUTH_HEADER)
  OM_AUTH_HEADER               en-tête "Basic xxxx" fourni par Orange (alternative)
  OM_ENV                        "dev" (test) ou "prod" (défaut : dev)
  OM_CURRENCY                   devise Orange (défaut : OUV en test, XOF en prod)
"""

import base64
import hashlib
import hmac
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal

from django.conf import settings
from django.urls import reverse

WAVE_BASE = "https://api.wave.com/v1"
OM_TOKEN_URL = "https://api.orange.com/oauth/v3/token"


class PaymentError(Exception):
    """Erreur générale lors d'un appel à une passerelle de paiement."""


class PaymentNotConfigured(PaymentError):
    """Les identifiants marchands ne sont pas configurés."""


# --------------------------------------------------------------------------- #
# Utilitaires
# --------------------------------------------------------------------------- #
def _env(name, default=""):
    return os.environ.get(name, default)


def wave_enabled():
    return bool(_env("WAVE_API_KEY"))


def om_enabled():
    return bool(_env("OM_MERCHANT_KEY") and (_env("OM_CONSUMER_KEY") or _env("OM_AUTH_HEADER")))


def any_gateway_enabled():
    return wave_enabled() or om_enabled()


def site_url(request):
    configured = _env("DRESSIT_SITE_URL") or getattr(settings, "DRESSIT_SITE_URL", "")
    if configured:
        return configured.rstrip("/")
    return request.build_absolute_uri("/").rstrip("/")


def _request(url, *, method="POST", headers=None, data=None, timeout=20):
    """Appel HTTP JSON. Retourne (code, dict). Lève PaymentError sur erreur réseau."""
    body = None
    if data is not None:
        body = json.dumps(data).encode() if isinstance(data, (dict, list)) else data
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode()
            return resp.status, (json.loads(payload) if payload else {})
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise PaymentError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise PaymentError(f"Réseau: {exc.reason}") from exc


def _amount_str(order):
    # Montants entiers en FCFA.
    return str(int(Decimal(order.total).to_integral_value()))


# --------------------------------------------------------------------------- #
# Wave
# --------------------------------------------------------------------------- #
def wave_create_session(order, request):
    """Crée une session de paiement Wave et retourne l'URL de redirection."""
    if not wave_enabled():
        raise PaymentNotConfigured("WAVE_API_KEY manquant.")
    base = site_url(request)
    payload = {
        "amount": _amount_str(order),
        "currency": "XOF",
        "success_url": f"{base}{reverse('payment_return', args=[order.id])}?gw=wave",
        "error_url": f"{base}{reverse('payment_cancel', args=[order.id])}",
        "client_reference": str(order.id),
    }
    headers = {
        "Authorization": f"Bearer {_env('WAVE_API_KEY')}",
        "Content-Type": "application/json",
    }
    _code, data = _request(f"{WAVE_BASE}/checkout/sessions", headers=headers, data=payload)
    session_id = data.get("id")
    launch = data.get("wave_launch_url")
    if not session_id or not launch:
        raise PaymentError(f"Réponse Wave inattendue: {data}")
    order.gateway_session_id = session_id
    order.save(update_fields=["gateway_session_id"])
    return launch


def wave_payment_status(order):
    """Interroge Wave pour l'état réel du paiement. Retourne succeeded/processing/…"""
    if not order.gateway_session_id:
        return None
    headers = {"Authorization": f"Bearer {_env('WAVE_API_KEY')}"}
    _code, data = _request(
        f"{WAVE_BASE}/checkout/sessions/{order.gateway_session_id}",
        method="GET",
        headers=headers,
    )
    return data.get("payment_status")


def wave_verify_webhook(raw_body, signature_header):
    """Vérifie la signature HMAC-SHA256 d'un webhook Wave."""
    secret = _env("WAVE_WEBHOOK_SECRET")
    if not secret or not signature_header:
        return False
    parts = dict(
        p.split("=", 1) for p in signature_header.split(",") if "=" in p
    )
    timestamp, given = parts.get("t"), parts.get("v1")
    if not timestamp or not given:
        return False
    signed = f"{timestamp}{raw_body}".encode()
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, given)


# --------------------------------------------------------------------------- #
# Orange Money (Web Payment)
# --------------------------------------------------------------------------- #
def _om_env():
    return _env("OM_ENV", "dev")


def _om_base():
    return f"https://api.orange.com/orange-money-webpay/{_om_env()}/v1"


def om_access_token():
    auth = _env("OM_AUTH_HEADER")
    if not auth:
        raw = f"{_env('OM_CONSUMER_KEY')}:{_env('OM_CONSUMER_SECRET')}".encode()
        auth = "Basic " + base64.b64encode(raw).decode()
    headers = {
        "Authorization": auth,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    _code, data = _request(
        OM_TOKEN_URL, headers=headers, data=b"grant_type=client_credentials"
    )
    token = data.get("access_token")
    if not token:
        raise PaymentError(f"Jeton OAuth Orange indisponible: {data}")
    return token


def om_create_payment(order, request):
    """Crée un paiement Orange Money et retourne l'URL de paiement."""
    if not om_enabled():
        raise PaymentNotConfigured("Identifiants Orange Money manquants.")
    token = om_access_token()
    base = site_url(request)
    default_currency = "OUV" if _om_env() == "dev" else "XOF"
    payload = {
        "merchant_key": _env("OM_MERCHANT_KEY"),
        "currency": _env("OM_CURRENCY", default_currency),
        "order_id": str(order.id),
        "amount": int(Decimal(order.total)),
        "return_url": f"{base}{reverse('payment_return', args=[order.id])}?gw=om",
        "cancel_url": f"{base}{reverse('payment_cancel', args=[order.id])}",
        "notif_url": f"{base}{reverse('om_webhook')}",
        "lang": "fr",
        "reference": f"DressIT #{order.id}",
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    _code, data = _request(f"{_om_base()}/webpayment", headers=headers, data=payload)
    payment_url = data.get("payment_url")
    if not payment_url:
        raise PaymentError(f"Réponse Orange Money inattendue: {data}")
    order.gateway_token = data.get("pay_token", "")
    order.gateway_notif_token = data.get("notif_token", "")
    order.save(update_fields=["gateway_token", "gateway_notif_token"])
    return payment_url


def om_payment_status(order):
    """Interroge Orange Money pour l'état réel du paiement (SUCCESS/FAILED/…)."""
    if not order.gateway_token:
        return None
    token = om_access_token()
    payload = {
        "order_id": str(order.id),
        "amount": int(Decimal(order.total)),
        "pay_token": order.gateway_token,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    _code, data = _request(f"{_om_base()}/transactionstatus", headers=headers, data=payload)
    return data.get("status")
