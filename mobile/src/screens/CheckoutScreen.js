import React, { useEffect, useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert, Linking,
} from "react-native";
import api from "../api";
import { colors, money } from "../theme";
import { useApp } from "../store";

const FIELDS = [
  ["full_name", "Nom complet"],
  ["email", "E-mail"],
  ["phone", "Téléphone"],
  ["address", "Adresse"],
  ["city", "Ville"],
  ["postal_code", "Code postal"],
  ["country", "Pays"],
];

export default function CheckoutScreen({ navigation }) {
  const { user, cart, cartSubtotal, clearCart } = useApp();
  const [form, setForm] = useState({ country: "Sénégal", full_name: user?.first_name || "", email: user?.email || "" });
  const [method, setMethod] = useState("cod");
  const [methods, setMethods] = useState({ wave: false, orange_money: false, cod: true });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get("/config/").then(({ data }) => {
      setMethods(data.payment_methods);
      if (data.payment_methods.wave) setMethod("wave");
    });
  }, []);

  if (!user) {
    return (
      <View style={s.center}>
        <Text style={s.info}>Connectez-vous pour passer commande.</Text>
        <TouchableOpacity style={s.btn} onPress={() => navigation.navigate("Compte")}>
          <Text style={s.btnTxt}>Se connecter</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async () => {
    setSubmitting(true);
    try {
      const items = cart.map((i) => ({
        product_id: i.product.id, quantity: i.quantity, size: i.size, color: i.color,
      }));
      const { data } = await api.post("/orders/create/", { ...form, items, payment_method: method });
      clearCart();
      if (data.payment_url) {
        Linking.openURL(data.payment_url);
        Alert.alert("Paiement", "Finalisez le paiement dans la page qui s'ouvre.");
      } else {
        Alert.alert("Merci !", `Commande #${data.id} enregistrée.`);
      }
      navigation.navigate("Compte");
    } catch (e) {
      Alert.alert("Erreur", e.response?.data?.detail || "Commande impossible.");
    }
    setSubmitting(false);
  };

  const options = [
    methods.wave && { key: "wave", label: "🌊 Wave" },
    methods.orange_money && { key: "orange_money", label: "🟠 Orange Money" },
    { key: "cod", label: "🏠 Paiement à la livraison" },
  ].filter(Boolean);

  return (
    <ScrollView style={s.screen} contentContainerStyle={{ padding: 16 }}>
      <Text style={s.h}>Livraison</Text>
      {FIELDS.map(([k, label]) => (
        <View key={k} style={s.field}>
          <Text style={s.label}>{label}</Text>
          <TextInput
            style={s.input}
            value={form[k] || ""}
            onChangeText={(v) => set(k, v)}
            placeholderTextColor={colors.textMuted}
            keyboardType={k === "email" ? "email-address" : k === "phone" ? "phone-pad" : "default"}
            autoCapitalize={k === "email" ? "none" : "sentences"}
          />
        </View>
      ))}

      <Text style={s.h}>Paiement</Text>
      {options.map((o) => (
        <TouchableOpacity key={o.key} style={[s.pay, method === o.key && s.payActive]} onPress={() => setMethod(o.key)}>
          <Text style={s.payTxt}>{o.label}</Text>
        </TouchableOpacity>
      ))}

      <View style={s.totalRow}>
        <Text style={s.totalLabel}>Sous-total</Text>
        <Text style={s.total}>{money(cartSubtotal)}</Text>
      </View>

      <TouchableOpacity style={[s.btn, submitting && { opacity: 0.6 }]} disabled={submitting} onPress={submit}>
        <Text style={s.btnTxt}>{submitting ? "Traitement…" : "✅ Confirmer la commande"}</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  center: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg, padding: 20 },
  info: { color: colors.textSoft, marginBottom: 16 },
  h: { color: colors.text, fontSize: 18, fontWeight: "700", marginTop: 14, marginBottom: 8 },
  field: { marginBottom: 10 },
  label: { color: colors.textSoft, marginBottom: 4, fontSize: 13 },
  input: { backgroundColor: colors.surface2, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, color: colors.text, borderWidth: 1, borderColor: colors.border },
  pay: { backgroundColor: colors.surface, borderRadius: 12, borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 10 },
  payActive: { borderColor: colors.gold, backgroundColor: colors.surface2 },
  payTxt: { color: colors.text, fontWeight: "600" },
  totalRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 16 },
  totalLabel: { color: colors.textSoft, fontSize: 16 },
  total: { color: colors.gold, fontSize: 20, fontWeight: "700" },
  btn: { backgroundColor: colors.gold, borderRadius: 30, paddingVertical: 15, alignItems: "center", marginTop: 20, marginBottom: 40 },
  btnTxt: { color: "#2a1d0c", fontWeight: "700", fontSize: 16 },
});
