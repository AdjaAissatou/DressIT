import React, { useEffect, useState, useCallback } from "react";
import {
  View, Text, FlatList, TextInput, TouchableOpacity, ActivityIndicator, StyleSheet,
} from "react-native";
import api from "../api";
import { colors } from "../theme";
import ProductCard from "../components/ProductCard";

const GENDERS = [
  { key: "", label: "Tout" },
  { key: "femme", label: "Femme" },
  { key: "homme", label: "Homme" },
];

export default function ProductsScreen({ navigation }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [gender, setGender] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/products/", { params: { q, gender } });
      setProducts(data.results || data);
    } catch (e) {
      setProducts([]);
    }
    setLoading(false);
  }, [q, gender]);

  useEffect(() => { load(); }, [gender]);

  return (
    <View style={s.screen}>
      <View style={s.searchRow}>
        <TextInput
          style={s.search}
          placeholder="Rechercher un article…"
          placeholderTextColor={colors.textMuted}
          value={q}
          onChangeText={setQ}
          onSubmitEditing={load}
          returnKeyType="search"
        />
        <TouchableOpacity style={s.searchBtn} onPress={load}>
          <Text style={s.searchBtnTxt}>🔎</Text>
        </TouchableOpacity>
      </View>

      <View style={s.tabs}>
        {GENDERS.map((g) => (
          <TouchableOpacity
            key={g.key}
            style={[s.tab, gender === g.key && s.tabActive]}
            onPress={() => setGender(g.key)}
          >
            <Text style={[s.tabTxt, gender === g.key && s.tabTxtActive]}>{g.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <ActivityIndicator color={colors.gold} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={products}
          keyExtractor={(item) => String(item.id)}
          numColumns={2}
          contentContainerStyle={{ padding: 6, paddingBottom: 30 }}
          renderItem={({ item }) => (
            <ProductCard
              product={item}
              onPress={() => navigation.navigate("Product", { slug: item.slug })}
            />
          )}
          ListEmptyComponent={<Text style={s.empty}>Aucun article trouvé.</Text>}
        />
      )}
    </View>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  searchRow: { flexDirection: "row", padding: 12, gap: 8 },
  search: {
    flex: 1, backgroundColor: colors.surface2, borderRadius: 24, paddingHorizontal: 16,
    color: colors.text, borderWidth: 1, borderColor: colors.border,
  },
  searchBtn: { backgroundColor: colors.gold, borderRadius: 24, paddingHorizontal: 16, justifyContent: "center" },
  searchBtnTxt: { fontSize: 16 },
  tabs: { flexDirection: "row", paddingHorizontal: 12, gap: 8, marginBottom: 4 },
  tab: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, backgroundColor: colors.surface2, borderWidth: 1, borderColor: colors.border },
  tabActive: { backgroundColor: colors.gold, borderColor: colors.gold },
  tabTxt: { color: colors.textSoft, fontWeight: "600" },
  tabTxtActive: { color: "#2a1d0c" },
  empty: { color: colors.textMuted, textAlign: "center", marginTop: 40 },
});
