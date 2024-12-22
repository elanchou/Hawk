import axios from 'axios';
import { Trade, Position, EquityData, OrderBook } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface TradeRequest {
    symbol: string;
    type: 'market' | 'limit';
    quantity: number;
    price?: number;
}

export const tradingService = {
    async getTrades(): Promise<Trade[]> {
        const response = await axios.get(`${API_URL}/trades`);
        return response.data;
    },
    
    async getPositions(): Promise<Position[]> {
        const response = await axios.get(`${API_URL}/positions`);
        return response.data;
    },
    
    async getEquityCurve(): Promise<EquityData[]> {
        const response = await axios.get(`${API_URL}/equity-curve`);
        return response.data;
    },
    
    async getMarketData(symbol: string, interval: string, limit: number = 1000) {
        const response = await axios.get(`${API_URL}/market-data`, {
            params: { symbol, interval, limit }
        });
        return response.data;
    },
    
    async getTechnicalIndicators(symbol: string, interval: string, limit: number = 1000) {
        const response = await axios.get(`${API_URL}/technical-indicators`, {
            params: { symbol, interval, limit }
        });
        return response.data;
    },
    
    async placeTrade(trade: TradeRequest): Promise<any> {
        const response = await axios.post(`${API_URL}/trades`, trade);
        return response.data;
    },
    
    async getOrderBook(exchange: string, symbol: string): Promise<OrderBook> {
        const response = await axios.get(`${API_URL}/orderbook`, {
            params: { exchange, symbol }
        });
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
        await axios.post(`${API_URL}/hft/start`, params);
    },
    
    async stopHFT(symbol: string): Promise<void> {
        await axios.post(`${API_URL}/hft/stop`, { symbol });
    },
    
    async getHFTStatus(symbol: string): Promise<any> {
        const response = await axios.get(`${API_URL}/hft/status`, {
            params: { symbol }
        });
        return response.data;
    }
}; 