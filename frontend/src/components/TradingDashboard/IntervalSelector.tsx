import React from 'react';
import { Select } from 'antd';

const { Option } = Select;

interface IntervalSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const IntervalSelector: React.FC<IntervalSelectorProps> = ({ value, onChange }) => {
  return (
    <Select value={value} onChange={onChange} style={{ width: 120 }}>
      <Option value="1m">1分钟</Option>
      <Option value="5m">5分钟</Option>
      <Option value="15m">15分钟</Option>
      <Option value="1h">1小时</Option>
      <Option value="4h">4小时</Option>
      <Option value="1d">1天</Option>
    </Select>
  );
}; 