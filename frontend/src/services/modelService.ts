import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const modelService = {
  async createModel(config: any) {
    const response = await axios.post(`${API_URL}/api/models`, config);
    return response.data;
  },

  async listModels() {
    const response = await axios.get(`${API_URL}/api/models`);
    return response.data;
  },

  async getModel(name: string) {
    const response = await axios.get(`${API_URL}/api/models/${name}`);
    return response.data;
  },

  async deleteModel(name: string) {
    const response = await axios.delete(`${API_URL}/api/models/${name}`);
    return response.data;
  },

  async trainModel(name: string, trainingConfig: any) {
    const response = await axios.post(
      `${API_URL}/api/models/${name}/train`,
      trainingConfig
    );
    return response.data;
  },

  async uploadModel(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(
      `${API_URL}/api/models/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }
}; 