import React from 'react';
import { Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';

export interface Position {
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
}

interface PositionListProps {
  positions: Position[];
}

export const PositionList: React.FC<PositionListProps> = ({ positions }) => {
  const columns: ColumnsType<Position> = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '持仓量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (quantity: number) => quantity.toFixed(4),
    },
    {
      title: '开仓价',
      dataIndex: 'entryPrice',
      key: 'entryPrice',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '当前价',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '未实现盈亏',
      dataIndex: 'unrealizedPnl',
      key: 'unrealizedPnl',
      render: (pnl: number) => (
        <span style={{ color: pnl >= 0 ? '#3f8600' : '#cf1322' }}>
          {pnl.toFixed(2)}
        </span>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={positions}
      rowKey="symbol"
      pagination={false}
      size="small"
    />
  );
}; 