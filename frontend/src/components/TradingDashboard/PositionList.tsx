import React from 'react';
import { Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { Position } from '../../types';

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
      dataIndex: 'entry_price',
      key: 'entry_price',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '当前价',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '未实现盈亏',
      dataIndex: 'unrealized_pnl',
      key: 'unrealized_pnl',
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