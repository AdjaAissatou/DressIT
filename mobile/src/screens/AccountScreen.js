import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import api from "../api";
import { colors, money } from "../theme";
import { useApp } from "../store";

export default function AccountScreen() {
  const { user, login, register, logout } = useApp();
  if (user) return <LoggedIn user={user} logout={logout} />;
  return <Auth login={login} register={register} />;
}

function Auth({ login, register }) {
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({});
  const [busy, setBusy] = useState(false);
  const set = (k, v) => setF((p) => ({ ...p, [k]: v }));

  const submit = async () => {
    setBusy(true);
    try {
      if (mode === "login") await login(f.username, f.password);
      else await register({ username: f.username, email: f.email, first_name: f.first_name, password: f.password });
    } catch (e) {
      Alert.alert("Erreur", e.response?.data?.detail || "Vérifiez vos informations.");
    }
    setBusy(false);
  };

  return (
    <ScrollView style={s.screen} contentContainerStyle={{ padding: 20 }}>
      <Text style={s.title}>{mode === "login" ? "Connexion" : "Créer un compte"}</Text>
      <Input label="Nom d'utilisateur" value={f.username} onChangeText={(v) => set("username", v)} autoCapitalize="none" />
      {mode === "register" && <Input label="Prénom" value={f.first_name} onChangeText={(v) => set("first_name", v)} />}
      {mode === "register" && <Input label="E-mail" value={f.email} onChangeText={(v) => set("email", v)} autoCapitalize="none" keyboardType="email-address" />}
      <Input label="Mot de passe" value={f.password} onChangeText={(v) => set("password", v)} secureTextEntry />
      <TouchableOpacity style={[s.btn, busy && { opacity: 0.6 }]} disabled={busy} onPress={submit}>
        <Text style={s.btnTxt}>{mode === "login" ? "Se connecter" : "Créer mon compte"}</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => setMode(mode === "login" ? "register" : "login")}>
        <Text style={s.switch}>
          {mode === "login" ? "Pas de compte ? Créer un compte" : "Déjà inscrit·e ? Se connecter"}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function LoggedIn({ user, logout }) {
  const [orders, setOrders] = useState([]);

  const load = useCallback(() => {
    api.get("/orders/").then(({ data }) => setOrders(data.results || data)).catch(() => {});
  }, []);
  useFocusEffect(useCallback(() => { load(); }, [load]));

  return (
    <ScrollView style={s.screen} contentContainerStyle={{ padding: 20 }}>
      <Text style={s.title}>Bonjour, {user.first_name || user.username} 👋</Text>
      <Text style={s.section}>Mes commandes</Text>
      {orders.length === 0 ? (
        <Text style={s.muted}>Aucune commande pour l'instant.</Text>
      ) : (
        orders.map((o) => (
          <View key={o.id} style={s.order}>
            <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
              <Text style={s.orderId}>Commande #{o.id}</Text>
              <Text style={s.status}>{o.status_display}</Text>
            </View>
            <Text style={s.muted}>{o.items.length} article(s) · {o.payment_method_display}</Text>
            <Text style={s.orderTotal}>{money(o.total)}</Text>
          </View>
        ))
      )}
      <TouchableOpacity style={[s.btn, { backgroundColor: colors.surface2, marginTop: 24 }]} onPress={logout}>
        <Text style={[s.btnTxt, { color: colors.text }]}>Déconnexion</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function Input({ label, ...props }) {
  return (
    <View style={{ marginBottom: 12 }}>
      <Text style={s.label}>{label}</Text>
      <TextInput style={s.input} placeholderTextColor={colors.textMuted} {...props} />
    </View>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  title: { color: colors.text, fontSize: 22, fontWeight: "700", marginBottom: 18 },
  label: { color: colors.textSoft, marginBottom: 4, fontSize: 13 },
  input: { backgroundColor: colors.surface2, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, color: colors.text, borderWidth: 1, borderColor: colors.border },
  btn: { backgroundColor: colors.gold, borderRadius: 30, paddingVertical: 15, alignItems: "center", marginTop: 14 },
  btnTxt: { color: "#2a1d0c", fontWeight: "700", fontSize: 16 },
  switch: { color: colors.gold, textAlign: "center", marginTop: 16 },
  section: { color: colors.text, fontSize: 18, fontWeight: "700", marginBottom: 10 },
  muted: { color: colors.textMuted },
  order: { backgroundColor: colors.surface, borderRadius: 14, borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 10 },
  orderId: { color: colors.text, fontWeight: "700" },
  status: { color: colors.gold, fontWeight: "600" },
  orderTotal: { color: colors.gold, fontSize: 18, fontWeight: "700", marginTop: 6 },
});
