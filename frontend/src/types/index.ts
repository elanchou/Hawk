export interface Trade {
    timestamp: string;
    type: 'buy' | 'sell';
    price: number;
    quantity: number;
    pnl?: number;
}

export interface Position {
    symbol: string;
    quantity: number;
    entry_price: number;
    current_price: number;
    unrealized_pnl: number;
}

export interface EquityData {
    timestamp: string;
    equity: number;
    cash: number;
    positions_value: number;
}

export interface OrderBook {
    bids: Array<[number, number]>;
    asks: Array<[number, number]>;
    timestamp: string;
}

export interface MarketData {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

export interface HFTStatus {
    running: boolean;
    symbol: string;
    position: number;
    trades_count: number;
    pnl: number;
} 