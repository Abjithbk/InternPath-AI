import axios from 'axios'
import { BASEURL } from './component/constants/constants'

const api = axios.create({
    baseURL:BASEURL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
export default api