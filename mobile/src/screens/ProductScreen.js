import React, { useEffect, useState } from "react";
import {
  View, Text, Image, ScrollView, TouchableOpacity, ActivityIndicator, StyleSheet, Alert,
} from "react-native";
import api from "../api";
import { colors, money } from "../theme";
import { useApp } from "../store";

export default function ProductScreen({ route, navigation }) {
  const { slug } = route.params;
  const { addToCart } = useApp();
  const [product, setProduct] = useState(null);
  const [size, setSize] = useState("");
  const [color, setColor] = useState("");
  const [mainImg, setMainImg] = useState(null);

  useEffect(() => {
    api.get(`/products/${slug}/`).then(({ data }) => {
      setProduct(data);
      setMainImg(data.image);
      if (data.sizes && data.sizes.length) setSize(data.sizes[0].label);
      if (data.colors && data.colors.length) setColor(data.colors[0].name);
    });
  }, [slug]);

  if (!product) return <ActivityIndicator color={colors.gold} style={{ flex: 1 }} />;

  const add = () => {
    addToCart(product, 1, size, color);
    Alert.alert("Panier", `« ${product.name} » ajouté au panier.`, [
      { text: "Continuer" },
      { text: "Voir le panier", onPress: () => navigation.navigate("Panier") },
    ]);
  };

  return (
    <ScrollView style={s.screen}>
      <View style={s.hero}>
        {mainImg ? <Image source={{ uri: mainImg }} style={s.heroImg} /> : <Text style={s.noPhoto}>👗</Text>}
      </View>
      {product.images && product.images.length > 1 ? (
        <ScrollView horizontal style={s.thumbs} showsHorizontalScrollIndicator={false}>
          {product.images.map((im) => (
            <TouchableOpacity key={im.id} onPress={() => setMainImg(im.url)}>
              <Image source={{ uri: im.url }} style={s.thumb} />
            </TouchableOpacity>
          ))}
        </ScrollView>
      ) : null}

      <View style={s.body}>
        <Text style={s.cat}>{product.category} · {product.gender}</Text>
        <Text style={s.name}>{product.name}</Text>
        <View style={s.priceRow}>
          <Text style={s.price}>{money(product.price)}</Text>
          {product.is_on_sale ? <Text style={s.old}>{money(product.compare_at_price)}</Text> : null}
        </View>

        {product.sizes && product.sizes.length ? (
          <>
            <Text style={s.label}>Taille</Text>
            <View style={s.pills}>
              {product.sizes.map((sz) => (
                <Pill key={sz.id} active={size === sz.label} onPress={() => setSize(sz.label)} label={sz.label} />
              ))}
            </View>
          </>
        ) : null}

        {product.colors && product.colors.length ? (
          <>
            <Text style={s.label}>Couleur</Text>
            <View style={s.pills}>
              {product.colors.map((cl) => (
                <Pill key={cl.id} active={color === cl.name} onPress={() => setColor(cl.name)} label={cl.name} dot={cl.hex_code} />
              ))}
            </View>
          </>
        ) : null}

        {product.description ? <Text style={s.desc}>{product.description}</Text> : null}

        <TouchableOpacity style={[s.btn, !product.in_stock && s.btnDisabled]} onPress={add} disabled={!product.in_stock}>
          <Text style={s.btnTxt}>{product.in_stock ? "🛍️  Ajouter au panier" : "Épuisé"}</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

function Pill({ active, onPress, label, dot }) {
  return (
    <TouchableOpacity style={[s.pill, active && s.pillActive]} onPress={onPress}>
      {dot ? <View style={[s.dot, { backgroundColor: dot }]} /> : null}
      <Text style={[s.pillTxt, active && s.pillTxtActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  hero: { aspectRatio: 0.85, backgroundColor: colors.surface2, alignItems: "center", justifyContent: "center" },
  heroImg: { width: "100%", height: "100%" },
  noPhoto: { fontSize: 70 },
  thumbs: { padding: 10 },
  thumb: { width: 64, height: 80, borderRadius: 8, marginRight: 8 },
  body: { padding: 16 },
  cat: { color: colors.textMuted, textTransform: "uppercase", fontSize: 11, letterSpacing: 1 },
  name: { color: colors.text, fontSize: 22, fontWeight: "700", marginVertical: 6 },
  priceRow: { flexDirection: "row", alignItems: "center" },
  price: { color: colors.gold, fontSize: 22, fontWeight: "700" },
  old: { color: colors.textMuted, textDecorationLine: "line-through", marginLeft: 10 },
  label: { color: colors.textSoft, fontWeight: "600", marginTop: 18, marginBottom: 8 },
  pills: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  pill: { flexDirection: "row", alignItems: "center", paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  pillActive: { backgroundColor: colors.gold, borderColor: colors.gold },
  pillTxt: { color: colors.text },
  pillTxtActive: { color: "#2a1d0c", fontWeight: "700" },
  dot: { width: 14, height: 14, borderRadius: 7, marginRight: 6, borderWidth: 1, borderColor: "#0003" },
  desc: { color: colors.textSoft, marginTop: 18, lineHeight: 21 },
  btn: { backgroundColor: colors.gold, borderRadius: 30, paddingVertical: 15, alignItems: "center", marginTop: 22 },
  btnDisabled: { backgroundColor: colors.surface2 },
  btnTxt: { color: "#2a1d0c", fontWeight: "700", fontSize: 16 },
});
