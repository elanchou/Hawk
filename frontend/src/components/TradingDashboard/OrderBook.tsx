import React from 'react';
import { Card, Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';

interface OrderBookProps {
  data: {
    bids: Array<[number, number]>;
    asks: Array<[number, number]>;
  };
}

interface OrderBookRow {
  price: number;
  amount: number;
  total: number;
}

export const OrderBook: React.FC<OrderBookProps> = ({ data }) => {
  const columns: ColumnsType<OrderBookRow> = [
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '数量',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => amount.toFixed(4),
    },
    {
      title: '累计',
      dataIndex: 'total',
      key: 'total',
      render: (total: number) => total.toFixed(4),
    },
  ];

  const processOrders = (orders: Array<[number, number]>) => {
    let total = 0;
    return orders.map(([price, amount]) => {
      total += amount;
      return {
        price,
        amount,
        total,
      };
    });
  };

  const asks = processOrders(data.asks.slice().reverse());
  const bids = processOrders(data.bids);

  return (
    <Card title="订单簿">
      <Table
        size="small"
        pagination={false}
        columns={columns}
        dataSource={[...asks, ...bids]}
        rowClassName={(record) => {
          const isAsk = asks.includes(record);
          return isAsk ? 'order-book-ask' : 'order-book-bid';
        }}
      />
    </Card>
  );
}; 