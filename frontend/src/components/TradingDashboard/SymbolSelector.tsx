import React from 'react';
import { Select } from 'antd';

const { Option } = Select;

interface SymbolSelectorProps {
  value: string;
  onChange: (value: string) => void;
  exchange: string;
}

export const SymbolSelector: React.FC<SymbolSelectorProps> = ({ value, onChange, exchange }) => {
  const symbols = exchange === 'okx' 
    ? ['BTC-USDT', 'ETH-USDT']
    : ['BTCUSDT', 'ETHUSDT'];

  return (
    <Select value={value} onChange={onChange} style={{ width: 120 }}>
      {symbols.map(symbol => (
        <Option key={symbol} value={symbol}>{symbol}</Option>
      ))}
    </Select>
  );
}; 