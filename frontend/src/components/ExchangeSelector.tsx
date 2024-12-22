import React from 'react';
import { Select, Space } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';

const { Option } = Select;

interface ExchangeSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const ExchangeSelector: React.FC<ExchangeSelectorProps> = ({ value, onChange }) => {
  return (
    <Space>
      <GlobalOutlined />
      <Select 
        value={value} 
        onChange={onChange}
        style={{ width: 120 }}
      >
        <Option value="okx">OKX</Option>
        <Option value="binance">Binance</Option>
      </Select>
    </Space>
  );
}; 