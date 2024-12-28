import React from 'react';
import { Card, Table, Statistic, Row, Col } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import type { BacktestResult } from '../../types';

interface BacktestResultsProps {
  results: BacktestResult | null;
}

export const BacktestResults: React.FC<BacktestResultsProps> = ({ results }) => {
  if (!results) {
    return <div>暂无回测结果</div>;
  }

  return (
    <>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总收益率" 
              value={results.total_return * 100} 
              precision={2}
              suffix="%" 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="夏普比率" 
              value={results.sharpe_ratio} 
              precision={2} 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="最大回撤" 
              value={results.max_drawdown * 100} 
              precision={2}
              suffix="%" 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="胜率" 
              value={results.win_rate * 100} 
              precision={2}
              suffix="%" 
            />
          </Card>
        </Col>
      </Row>

      <Card title="权益曲线" style={{ marginTop: 16 }}>
        <LineChart
          width={800}
          height={400}
          data={results.equity_curve}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="equity" stroke="#8884d8" />
        </LineChart>
      </Card>

      <Card title="交易记录" style={{ marginTop: 16 }}>
        <Table
          dataSource={results.trades}
          columns={[
            {
              title: '时间',
              dataIndex: 'timestamp',
              key: 'timestamp',
            },
            {
              title: '类型',
              dataIndex: 'type',
              key: 'type',
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
              render: (pnl: number) => (
                <span style={{ color: pnl >= 0 ? '#52c41a' : '#f5222d' }}>
                  {pnl.toFixed(2)}
                </span>
              ),
            },
          ]}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </>
  );
}; 