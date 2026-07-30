import React from "react";
import { Text } from "react-native";
import { NavigationContainer, DefaultTheme } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { StatusBar } from "expo-status-bar";

import { AppProvider, useApp } from "./src/store";
import { colors } from "./src/theme";
import ProductsScreen from "./src/screens/ProductsScreen";
import ProductScreen from "./src/screens/ProductScreen";
import PhotoSearchScreen from "./src/screens/PhotoSearchScreen";
import CartScreen from "./src/screens/CartScreen";
import CheckoutScreen from "./src/screens/CheckoutScreen";
import AccountScreen from "./src/screens/AccountScreen";

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: colors.bg,
    card: colors.brownDark,
    text: colors.white,
    border: colors.border,
    primary: colors.gold,
  },
};

const screenOpts = {
  headerStyle: { backgroundColor: colors.brownDark },
  headerTintColor: colors.white,
  headerTitleStyle: { fontWeight: "700" },
};

function Icon({ emoji, focused }) {
  return <Text style={{ fontSize: focused ? 22 : 18, opacity: focused ? 1 : 0.6 }}>{emoji}</Text>;
}

function Tabs() {
  const { cartCount } = useApp();
  return (
    <Tab.Navigator
      screenOptions={{
        ...screenOpts,
        tabBarStyle: { backgroundColor: colors.brownDark, borderTopColor: colors.border },
        tabBarActiveTintColor: colors.gold,
        tabBarInactiveTintColor: colors.textMuted,
      }}
    >
      <Tab.Screen
        name="Boutique"
        component={ProductsScreen}
        options={{ title: "DressIT", tabBarIcon: ({ focused }) => <Icon emoji="🛍️" focused={focused} /> }}
      />
      <Tab.Screen
        name="Photo"
        component={PhotoSearchScreen}
        options={{ title: "Recherche photo", tabBarIcon: ({ focused }) => <Icon emoji="📷" focused={focused} /> }}
      />
      <Tab.Screen
        name="Panier"
        component={CartScreen}
        options={{
          tabBarBadge: cartCount || undefined,
          tabBarIcon: ({ focused }) => <Icon emoji="🛒" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Compte"
        component={AccountScreen}
        options={{ tabBarIcon: ({ focused }) => <Icon emoji="👤" focused={focused} /> }}
      />
    </Tab.Navigator>
  );
}

function Root() {
  const { ready } = useApp();
  if (!ready) return null;
  return (
    <NavigationContainer theme={navTheme}>
      <StatusBar style="light" />
      <Stack.Navigator screenOptions={screenOpts}>
        <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
        <Stack.Screen name="Product" component={ProductScreen} options={{ title: "Article" }} />
        <Stack.Screen name="Checkout" component={CheckoutScreen} options={{ title: "Commander" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <AppProvider>
      <Root />
    </AppProvider>
  );
}
