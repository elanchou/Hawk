import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import styled from '@emotion/styled';
import { TradeList, Trade } from './TradeList';
import { EquityChart, EquityData } from './EquityChart';
import { PositionList, Position } from './PositionList';
import { fetchTrades, fetchPositions, fetchEquityCurve } from '../../services/api';

const DashboardContainer = styled.div`
  .ant-card {
    height: 100%;
  }
`;

const TradingDashboard: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [equityCurve, setEquityCurve] = useState<EquityData[]>([]);
  const [dailyPnl, setDailyPnl] = useState<number>(0);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [tradesData, positionsData, equityData] = await Promise.all([
          fetchTrades(),
          fetchPositions(),
          fetchEquityCurve(),
        ]);
        setTrades(tradesData);
        setPositions(positionsData);
        setEquityCurve(equityData);

        // 计算今日盈亏
        if (equityData.length >= 2) {
          const todayStart = equityData[equityData.length - 2].equity;
          const current = equityData[equityData.length - 1].equity;
          setDailyPnl(current - todayStart);
        }
      } catch (error) {
        console.error('Failed to load data:', error);
      }
    };

    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <DashboardContainer>
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card>
            <Statistic
              title="账户总值"
              value={equityCurve[equityCurve.length - 1]?.equity || 0}
              precision={2}
              prefix="$"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="今日盈亏"
              value={dailyPnl}
              precision={2}
              prefix="$"
              valueStyle={{ color: dailyPnl >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="持仓数量"
              value={positions.length}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="权益曲线">
            <EquityChart data={equityCurve} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="当前持仓">
            <PositionList positions={positions} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="最近交易">
            <TradeList trades={trades} />
          </Card>
        </Col>
      </Row>
    </DashboardContainer>
  );
};

export default TradingDashboard; 