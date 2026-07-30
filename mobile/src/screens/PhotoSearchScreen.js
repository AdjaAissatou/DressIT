import React, { useState } from "react";
import {
  View, Text, TouchableOpacity, FlatList, Image, ActivityIndicator, StyleSheet,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import api from "../api";
import { colors } from "../theme";
import ProductCard from "../components/ProductCard";

export default function PhotoSearchScreen({ navigation }) {
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const pick = async (fromCamera) => {
    const perm = fromCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) return;
    const res = fromCamera
      ? await ImagePicker.launchCameraAsync({ quality: 0.7 })
      : await ImagePicker.launchImageLibraryAsync({ quality: 0.7 });
    if (res.canceled) return;
    const asset = res.assets[0];
    setPreview(asset.uri);
    search(asset);
  };

  const search = async (asset) => {
    setLoading(true);
    setResults(null);
    try {
      const form = new FormData();
      form.append("photo", {
        uri: asset.uri,
        name: "photo.jpg",
        type: "image/jpeg",
      });
      const { data } = await api.post("/products/search-photo/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResults(data.results);
    } catch (e) {
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <View style={s.screen}>
      <FlatList
        data={results || []}
        keyExtractor={(item) => String(item.id)}
        numColumns={2}
        contentContainerStyle={{ padding: 6, paddingBottom: 30 }}
        ListHeaderComponent={
          <View style={s.header}>
            <Text style={s.title}>📷 Recherche par photo</Text>
            <Text style={s.sub}>Prenez ou choisissez la photo d'un vêtement.</Text>
            {preview ? <Image source={{ uri: preview }} style={s.preview} /> : null}
            <View style={s.btns}>
              <TouchableOpacity style={s.btn} onPress={() => pick(true)}>
                <Text style={s.btnTxt}>📸 Caméra</Text>
              </TouchableOpacity>
              <TouchableOpacity style={s.btn} onPress={() => pick(false)}>
                <Text style={s.btnTxt}>🖼️ Galerie</Text>
              </TouchableOpacity>
            </View>
            {loading ? <ActivityIndicator color={colors.gold} style={{ marginTop: 20 }} /> : null}
            {results && results.length ? <Text style={s.results}>Articles similaires</Text> : null}
            {results && results.length === 0 ? <Text style={s.sub}>Aucun article ressemblant.</Text> : null}
          </View>
        }
        renderItem={({ item }) => (
          <ProductCard product={item} onPress={() => navigation.navigate("Product", { slug: item.slug })} />
        )}
      />
    </View>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  header: { padding: 10, alignItems: "center" },
  title: { color: colors.text, fontSize: 20, fontWeight: "700", marginTop: 8 },
  sub: { color: colors.textMuted, marginTop: 4, textAlign: "center" },
  preview: { width: 180, height: 220, borderRadius: 14, marginTop: 14 },
  btns: { flexDirection: "row", gap: 12, marginTop: 16 },
  btn: { backgroundColor: colors.gold, borderRadius: 24, paddingHorizontal: 22, paddingVertical: 12 },
  btnTxt: { color: "#2a1d0c", fontWeight: "700" },
  results: { color: colors.text, fontWeight: "700", fontSize: 16, marginTop: 22, alignSelf: "flex-start" },
});
