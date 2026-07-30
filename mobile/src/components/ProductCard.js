import React from "react";
import { View, Text, Image, TouchableOpacity, StyleSheet } from "react-native";
import { colors, money } from "../theme";

export default function ProductCard({ product, onPress }) {
  return (
    <TouchableOpacity style={s.card} onPress={onPress} activeOpacity={0.85}>
      <View style={s.thumb}>
        {product.image ? (
          <Image source={{ uri: product.image }} style={s.img} />
        ) : (
          <Text style={s.noPhoto}>👗</Text>
        )}
        {product.is_on_sale ? (
          <View style={s.badge}>
            <Text style={s.badgeTxt}>-{product.discount_percent}%</Text>
          </View>
        ) : null}
        {!product.in_stock ? (
          <View style={[s.badge, s.badgeOut]}>
            <Text style={s.badgeTxt}>Épuisé</Text>
          </View>
        ) : null}
      </View>
      <View style={s.info}>
        <Text style={s.cat}>{product.category}</Text>
        <Text style={s.name} numberOfLines={2}>{product.name}</Text>
        <View style={s.priceRow}>
          <Text style={s.price}>{money(product.price)}</Text>
          {product.is_on_sale ? (
            <Text style={s.old}>{money(product.compare_at_price)}</Text>
          ) : null}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  card: {
    flex: 1, margin: 6, backgroundColor: colors.surface,
    borderRadius: 14, borderWidth: 1, borderColor: colors.border, overflow: "hidden",
  },
  thumb: { aspectRatio: 0.8, backgroundColor: colors.surface2, alignItems: "center", justifyContent: "center" },
  img: { width: "100%", height: "100%" },
  noPhoto: { fontSize: 40 },
  badge: { position: "absolute", top: 8, left: 8, backgroundColor: colors.gold, borderRadius: 12, paddingHorizontal: 8, paddingVertical: 3 },
  badgeOut: { backgroundColor: "#6b6b6b" },
  badgeTxt: { color: "#2a1d0c", fontWeight: "700", fontSize: 11 },
  info: { padding: 10 },
  cat: { color: colors.textMuted, fontSize: 10, textTransform: "uppercase", letterSpacing: 1 },
  name: { color: colors.text, fontWeight: "600", marginTop: 2 },
  priceRow: { flexDirection: "row", alignItems: "center", marginTop: 6 },
  price: { color: colors.gold, fontWeight: "700", fontSize: 15 },
  old: { color: colors.textMuted, textDecorationLine: "line-through", fontSize: 12, marginLeft: 8 },
});
