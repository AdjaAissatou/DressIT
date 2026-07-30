import React from "react";
import { View, Text, Image, FlatList, TouchableOpacity, StyleSheet } from "react-native";
import { colors, money } from "../theme";
import { useApp } from "../store";

export default function CartScreen({ navigation }) {
  const { cart, setQuantity, removeFromCart, cartSubtotal } = useApp();

  if (!cart.length) {
    return (
      <View style={s.empty}>
        <Text style={{ fontSize: 50 }}>🛍️</Text>
        <Text style={s.emptyTxt}>Votre panier est vide.</Text>
        <TouchableOpacity style={s.cta} onPress={() => navigation.navigate("Boutique")}>
          <Text style={s.ctaTxt}>Découvrir la boutique</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={s.screen}>
      <FlatList
        data={cart}
        keyExtractor={(_, i) => String(i)}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item, index }) => (
          <View style={s.row}>
            {item.product.image ? (
              <Image source={{ uri: item.product.image }} style={s.thumb} />
            ) : (
              <View style={[s.thumb, s.noPhoto]}><Text>👗</Text></View>
            )}
            <View style={{ flex: 1, marginLeft: 12 }}>
              <Text style={s.name}>{item.product.name}</Text>
              {item.size ? <Text style={s.meta}>Taille : {item.size}</Text> : null}
              {item.color ? <Text style={s.meta}>Couleur : {item.color}</Text> : null}
              <View style={s.qtyRow}>
                <TouchableOpacity style={s.qtyBtn} onPress={() => setQuantity(index, item.quantity - 1)}>
                  <Text style={s.qtyBtnTxt}>−</Text>
                </TouchableOpacity>
                <Text style={s.qty}>{item.quantity}</Text>
                <TouchableOpacity style={s.qtyBtn} onPress={() => setQuantity(index, item.quantity + 1)}>
                  <Text style={s.qtyBtnTxt}>+</Text>
                </TouchableOpacity>
              </View>
            </View>
            <View style={{ alignItems: "flex-end" }}>
              <Text style={s.price}>{money(item.product.price * item.quantity)}</Text>
              <TouchableOpacity onPress={() => removeFromCart(index)}>
                <Text style={s.remove}>🗑 Retirer</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      />
      <View style={s.footer}>
        <View style={s.totalRow}>
          <Text style={s.totalLabel}>Sous-total</Text>
          <Text style={s.total}>{money(cartSubtotal)}</Text>
        </View>
        <TouchableOpacity style={s.checkout} onPress={() => navigation.navigate("Checkout")}>
          <Text style={s.checkoutTxt}>Passer commande →</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  empty: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg },
  emptyTxt: { color: colors.textMuted, marginTop: 10 },
  cta: { backgroundColor: colors.gold, borderRadius: 24, paddingHorizontal: 20, paddingVertical: 12, marginTop: 16 },
  ctaTxt: { color: "#2a1d0c", fontWeight: "700" },
  row: { flexDirection: "row", backgroundColor: colors.surface, borderRadius: 14, borderWidth: 1, borderColor: colors.border, padding: 10, marginBottom: 10 },
  thumb: { width: 70, height: 88, borderRadius: 8, backgroundColor: colors.surface2 },
  noPhoto: { alignItems: "center", justifyContent: "center" },
  name: { color: colors.text, fontWeight: "600" },
  meta: { color: colors.textMuted, fontSize: 12 },
  qtyRow: { flexDirection: "row", alignItems: "center", marginTop: 8 },
  qtyBtn: { width: 32, height: 32, borderRadius: 16, backgroundColor: colors.surface2, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: colors.border },
  qtyBtnTxt: { color: colors.text, fontSize: 18 },
  qty: { color: colors.text, marginHorizontal: 14, fontSize: 16 },
  price: { color: colors.gold, fontWeight: "700" },
  remove: { color: colors.textMuted, fontSize: 12, marginTop: 10 },
  footer: { padding: 16, borderTopWidth: 1, borderTopColor: colors.border, backgroundColor: colors.bgAlt },
  totalRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 12 },
  totalLabel: { color: colors.textSoft, fontSize: 16 },
  total: { color: colors.gold, fontSize: 20, fontWeight: "700" },
  checkout: { backgroundColor: colors.gold, borderRadius: 30, paddingVertical: 15, alignItems: "center" },
  checkoutTxt: { color: "#2a1d0c", fontWeight: "700", fontSize: 16 },
});
