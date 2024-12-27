import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Space } from 'antd';
import { ExchangeSelector } from '../ExchangeSelector';
import { MarketChart } from './MarketChart';
import { TradeControl } from './TradeControl';
import { HFTControl } from '../HFTControl';
import { OrderBook } from './OrderBook';
import { TradeList } from './TradeList';
import { PositionList } from './PositionList';
import { EquityChart } from './EquityChart';
import { tradingService } from '../../services/tradingService';
import { SymbolSelector } from './SymbolSelector';
import { IntervalSelector } from './IntervalSelector';
import type { Trade, Position, EquityData, OrderBook as OrderBookType } from '../../types';

interface MarketData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface DashboardData {
  trades: Trade[];
  positions: Position[];
  equity: EquityData[];
  marketData: MarketData[];
  orderBook: OrderBookType;
}

export const TradingDashboard: React.FC = () => {
  const [exchange, setExchange] = useState('okx');
  const [symbol, setSymbol] = useState('BTC-USDT');
  const [interval, setInterval] = useState('1m');
  const [data, setData] = useState<DashboardData>({
    trades: [],
    positions: [],
    equity: [],
    marketData: [],
    orderBook: { bids: [], asks: [], timestamp: '' }
  });

  const loadData = async () => {
    try {
      const [
        trades,
        positions,
        equity,
        marketData,
        orderBook
      ] = await Promise.all([
        tradingService.getTrades(),
        tradingService.getPositions(),
        tradingService.getEquityCurve(),
        tradingService.getMarketData(symbol, interval),
        tradingService.getOrderBook(exchange, symbol)
      ]);

      setData({
        trades,
        positions,
        equity,
        marketData,
        orderBook
      });
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  useEffect(() => {
    loadData();
    const intervalId = window.setInterval(() => {
      loadData();
    }, 1000);
    return () => clearInterval(intervalId);
  }, [exchange, symbol, interval]);

  return (
    <div className="trading-dashboard">
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <Space>
              <ExchangeSelector value={exchange} onChange={setExchange} />
              <SymbolSelector value={symbol} onChange={setSymbol} exchange={exchange} />
              <IntervalSelector value={interval} onChange={setInterval} />
            </Space>
          </Card>
        </Col>

        <Col span={16}>
          <MarketChart 
            data={data.marketData}
            indicators={[]}
          />
        </Col>

        <Col span={8}>
          <OrderBook data={data.orderBook} />
        </Col>

        <Col span={12}>
          <TradeControl 
            symbol={symbol}
            exchange={exchange}
            onTrade={loadData}
          />
        </Col>

        <Col span={12}>
          <HFTControl 
            symbol={symbol}
            exchange={exchange}
          />
        </Col>

        <Col span={24}>
          <EquityChart data={data.equity} />
        </Col>

        <Col span={12}>
          <Card title="持仓">
            <PositionList positions={data.positions} />
          </Card>
        </Col>

        <Col span={12}>
          <Card title="交易记录">
            <TradeList trades={data.trades} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}; 