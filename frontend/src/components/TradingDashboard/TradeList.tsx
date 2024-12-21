import React from 'react';
import { Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';

export interface Trade {
  timestamp: string;
  type: 'buy' | 'sell';
  price: number;
  quantity: number;
  pnl?: number;
}

interface TradeListProps {
  trades: Trade[];
}

export const TradeList: React.FC<TradeListProps> = ({ trades }) => {
  const columns: ColumnsType<Trade> = [
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
          {type === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (quantity: number) => quantity.toFixed(4),
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (pnl?: number) => 
        pnl ? (
          <span style={{ color: pnl >= 0 ? '#3f8600' : '#cf1322' }}>
            {pnl.toFixed(2)}
          </span>
        ) : '-',
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={trades}
      rowKey="timestamp"
      pagination={{ pageSize: 5 }}
      size="small"
    />
  );
}; 