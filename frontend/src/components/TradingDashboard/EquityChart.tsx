import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import moment from 'moment';

export interface EquityData {
  timestamp: string;
  equity: number;
}

interface EquityChartProps {
  data: EquityData[];
}

export const EquityChart: React.FC<EquityChartProps> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="timestamp"
          tickFormatter={(value) => moment(value).format('MM-DD HH:mm')}
        />
        <YAxis />
        <Tooltip 
          labelFormatter={(value) => moment(value).format('YYYY-MM-DD HH:mm:ss')}
          formatter={(value: number) => [value.toFixed(2), '权益']}
        />
        <Line
          type="monotone"
          dataKey="equity"
          stroke="#8884d8"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}; 