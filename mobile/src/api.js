import axios from "axios";
import Constants from "expo-constants";
import AsyncStorage from "@react-native-async-storage/async-storage";

// URL de l'API Django. En développement, remplacez par l'IP de votre machine
// sur le réseau local (ex: http://192.168.1.10:8000/api) — "localhost" ne
// fonctionne pas depuis un téléphone. Réglable dans app.json > extra.apiUrl.
export const API_URL =
  (Constants.expoConfig &&
    Constants.expoConfig.extra &&
    Constants.expoConfig.extra.apiUrl) ||
  "http://192.168.1.10:8000/api";

const api = axios.create({ baseURL: API_URL, timeout: 20000 });

// Injecte le jeton d'authentification s'il existe.
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("token");
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

export default api;
