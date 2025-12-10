import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Configurar interceptor para incluir el token
const api = axios.create({
    baseURL: API_URL,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export interface UserProfile {
    id: string;
    nombres: string;
    apellidos: string;
    correo_institucional: string;
    rol: string;
    estado_cuenta: string;
    telefono?: string;
    descripcion?: string;
    perfil_url?: string;
    portada_url?: string;
    fecha_creacion: string;
    ultimo_acceso?: string;
    email_verified: boolean;
    twofa_enabled: boolean;
}

export interface UserUpdateData {
    nombres?: string;
    apellidos?: string;
    telefono?: string;
    descripcion?: string;
}

export const userService = {
    getMe: async (): Promise<UserProfile> => {
        const response = await api.get<UserProfile>('/auth/me');
        return response.data;
    },

    getUser: async (userId: string): Promise<UserProfile> => {
        const response = await api.get<UserProfile>(`/users/${userId}`);
        return response.data;
    },

    updateProfile: async (data: UserUpdateData): Promise<UserProfile> => {
        const response = await api.put<UserProfile>('/users/me', data);
        return response.data;
    },

    uploadAvatar: async (file: File): Promise<{ url: string }> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post<{ url: string }>('/perfil/foto-perfil/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    uploadBanner: async (file: File): Promise<{ url: string }> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post<{ url: string }>('/perfil/banner/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
};
