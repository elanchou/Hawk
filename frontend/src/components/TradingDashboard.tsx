import React, { useState, useEffect } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from 'recharts';
import { Table, Tag, Space, Button, Card, Statistic, Row, Col } from 'antd';

interface Trade {
    timestamp: string;
    type: string;
    price: number;
    quantity: number;
    pnl?: number;
}

interface Position {
    symbol: string;
    quantity: number;
    entryPrice: number;
    currentPrice: number;
    unrealizedPnl: number;
}

const TradingDashboard: React.FC = () => {
    const [trades, setTrades] = useState<Trade[]>([]);
    const [positions, setPositions] = useState<Position[]>([]);
    const [equityCurve, setEquityCurve] = useState<any[]>([]);
    
    useEffect(() => {
        // 获取交易数据
        fetchTrades();
        // 获取持仓数据
        fetchPositions();
        // 获取权益曲线数据
        fetchEquityCurve();
        
        // 设置定时刷新
        const timer = setInterval(() => {
            fetchTrades();
            fetchPositions();
            fetchEquityCurve();
        }, 5000);
        
        return () => clearInterval(timer);
    }, []);
    
    const fetchTrades = async () => {
        try {
            const response = await fetch('/api/trades');
            const data = await response.json();
            setTrades(data);
        } catch (error) {
            console.error('获取交易记录失败:', error);
        }
    };
    
    const fetchPositions = async () => {
        try {
            const response = await fetch('/api/positions');
            const data = await response.json();
            setPositions(data);
        } catch (error) {
            console.error('获取持仓数据失败:', error);
        }
    };
    
    const fetchEquityCurve = async () => {
        try {
            const response = await fetch('/api/equity-curve');
            const data = await response.json();
            setEquityCurve(data);
        } catch (error) {
            console.error('获取权益曲线失败:', error);
        }
    };
    
    const columns = [
        {
            title: '时间',
            dataIndex: 'timestamp',
            key: 'timestamp',
        },
        {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
            render: (type: string) => (
                <Tag color={type === 'buy' ? 'green' : 'red'}>
                    {type.toUpperCase()}
                </Tag>
            ),
        },
        {
            title: '价格',
            dataIndex: 'price',
            key: 'price',
        },
        {
            title: '数量',
            dataIndex: 'quantity',
            key: 'quantity',
        },
        {
            title: '盈亏',
            dataIndex: 'pnl',
            key: 'pnl',
            render: (pnl?: number) => (
                pnl ? (
                    <span style={{ color: pnl >= 0 ? 'green' : 'red' }}>
                        {pnl.toFixed(2)}
                    </span>
                ) : '-'
            ),
        },
    ];
    
    const calculateDailyPnl = () => {
        // 计算今日盈亏的逻辑
        return 0; // 替换为实际计算逻辑
    };
    
    return (
        <div className="trading-dashboard">
            <Row gutter={16}>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="总资产"
                            value={equityCurve[equityCurve.length - 1]?.equity}
                            precision={2}
                            prefix="$"
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="持仓数量"
                            value={positions.length}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="今日盈亏"
                            value={calculateDailyPnl()}
                            precision={2}
                            prefix="$"
                            valueStyle={{ color: calculateDailyPnl() >= 0 ? 'green' : 'red' }}
                        />
                    </Card>
                </Col>
            </Row>
            
            <Card title="权益曲线" style={{ marginTop: 16 }}>
                <LineChart
                    width={800}
                    height={400}
                    data={equityCurve}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="equity" stroke="#8884d8" />
                </LineChart>
            </Card>
            
            <Card title="交易记录" style={{ marginTop: 16 }}>
                <Table
                    columns={columns}
                    dataSource={trades}
                    rowKey="timestamp"
                    pagination={{ pageSize: 10 }}
                />
            </Card>
            
            <Card title="当前持仓" style={{ marginTop: 16 }}>
                <Table
                    columns={[
                        {
                            title: '交易对',
                            dataIndex: 'symbol',
                            key: 'symbol',
                        },
                        {
                            title: '持仓量',
                            dataIndex: 'quantity',
                            key: 'quantity',
                        },
                        {
                            title: '开仓价',
                            dataIndex: 'entryPrice',
                            key: 'entryPrice',
                        },
                        {
                            title: '当前价',
                            dataIndex: 'currentPrice',
                            key: 'currentPrice',
                        },
                        {
                            title: '未实现盈亏',
                            dataIndex: 'unrealizedPnl',
                            key: 'unrealizedPnl',
                            render: (pnl: number) => (
                                <span style={{ color: pnl >= 0 ? 'green' : 'red' }}>
                                    {pnl.toFixed(2)}
                                </span>
                            ),
                        },
                    ]}
                    dataSource={positions}
                    rowKey="symbol"
                    pagination={false}
                />
            </Card>
        </div>
    );
};

export default TradingDashboard; 