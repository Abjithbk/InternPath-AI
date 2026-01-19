import axios from 'axios'
import { BASEURL } from './component/constants/constants'

const api = axios.create({
    baseURL:BASEURL,
});

export default api