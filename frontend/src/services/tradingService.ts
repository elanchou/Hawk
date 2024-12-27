import axios from 'axios';
import { Trade, Position, EquityData, OrderBook } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const tradingService = {
  async getTrades(): Promise<Trade[]> {
    const response = await axios.get(`${API_URL}/api/trades`);
    return response.data;
  },

  async getPositions(): Promise<Position[]> {
    const response = await axios.get(`${API_URL}/api/positions`);
    return response.data;
  },

  async getEquityCurve(): Promise<EquityData[]> {
    const response = await axios.get(`${API_URL}/api/equity-curve`);
    return response.data;
  },

  async getMarketData(symbol: string, interval: string): Promise<any[]> {
    const response = await axios.get(`${API_URL}/api/market-data`, {
      params: { symbol, interval }
    });
    return response.data;
  },

  async getOrderBook(exchange: string, symbol: string): Promise<OrderBook> {
    const response = await axios.get(`${API_URL}/api/orderbook`, {
      params: { exchange, symbol }
    });
    return response.data;
  },

  async placeTrade(params: {
    symbol: string;
    type: 'market' | 'limit';
    side: 'buy' | 'sell';
    quantity: number;
    price?: number;
  }): Promise<any> {
    const response = await axios.post(`${API_URL}/api/trades`, params);
    return response.data;
  },

  async startHFT(params: {
    symbol: string;
    exchange: string;
    tick_interval: number;
    position_limit: number;
    min_spread: number;
    min_profit: number;
  }): Promise<void> {
    await axios.post(`${API_URL}/api/hft/start`, params);
  },

  async stopHFT(symbol: string): Promise<void> {
    await axios.post(`${API_URL}/api/hft/stop`, { symbol });
  }
}; 