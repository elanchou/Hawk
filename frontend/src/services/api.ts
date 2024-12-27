import axios from 'axios';
import type { Trade } from '../components/TradingDashboard/TradeList';
import type { Position } from '../types';
import type { EquityData } from '../components/TradingDashboard/EquityChart';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});

export const fetchTrades = async (): Promise<Trade[]> => {
  const response = await api.get<Trade[]>('/api/trades');
  return response.data;
};

export const fetchPositions = async (): Promise<Position[]> => {
  const response = await api.get<Position[]>('/api/positions');
  return response.data;
};

export const fetchEquityCurve = async (): Promise<EquityData[]> => {
  const response = await api.get<EquityData[]>('/api/equity-curve');
  return response.data;
}; 