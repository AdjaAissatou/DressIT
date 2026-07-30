// Contextes globaux : authentification + panier (persistés).
import React, { createContext, useContext, useEffect, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import api from "./api";

const AppContext = createContext(null);
export const useApp = () => useContext(AppContext);

export function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [cart, setCart] = useState([]); // [{product, quantity, size, color}]
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      const token = await AsyncStorage.getItem("token");
      const savedCart = await AsyncStorage.getItem("cart");
      if (savedCart) setCart(JSON.parse(savedCart));
      if (token) {
        try {
          const { data } = await api.get("/auth/me/");
          setUser(data);
        } catch (e) {
          await AsyncStorage.removeItem("token");
        }
      }
      setReady(true);
    })();
  }, []);

  const persistCart = async (next) => {
    setCart(next);
    await AsyncStorage.setItem("cart", JSON.stringify(next));
  };

  const login = async (username, password) => {
    const { data } = await api.post("/auth/login/", { username, password });
    await AsyncStorage.setItem("token", data.token);
    setUser(data.user);
    return data.user;
  };

  const register = async (payload) => {
    const { data } = await api.post("/auth/register/", payload);
    await AsyncStorage.setItem("token", data.token);
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    await AsyncStorage.removeItem("token");
    setUser(null);
  };

  const addToCart = (product, quantity = 1, size = "", color = "") => {
    const key = `${product.id}|${size}|${color}`;
    const existing = cart.find(
      (i) => `${i.product.id}|${i.size}|${i.color}` === key
    );
    let next;
    if (existing) {
      next = cart.map((i) =>
        i === existing ? { ...i, quantity: i.quantity + quantity } : i
      );
    } else {
      next = [...cart, { product, quantity, size, color }];
    }
    persistCart(next);
  };

  const setQuantity = (index, quantity) => {
    const next = cart
      .map((i, idx) => (idx === index ? { ...i, quantity } : i))
      .filter((i) => i.quantity > 0);
    persistCart(next);
  };

  const removeFromCart = (index) =>
    persistCart(cart.filter((_, idx) => idx !== index));

  const clearCart = () => persistCart([]);

  const cartCount = cart.reduce((s, i) => s + i.quantity, 0);
  const cartSubtotal = cart.reduce(
    (s, i) => s + Number(i.product.price) * i.quantity,
    0
  );

  return (
    <AppContext.Provider
      value={{
        user, ready, login, register, logout,
        cart, addToCart, setQuantity, removeFromCart, clearCart,
        cartCount, cartSubtotal,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}
