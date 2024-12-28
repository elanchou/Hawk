import React from 'react';
import { Form, InputNumber, DatePicker, Button, Select } from 'antd';
import type { ModelLayer } from '../../types';
import { modelService } from '../../services/modelService';

interface BacktestConfigProps {
  model: ModelLayer[];
  onBacktestComplete: (results: any) => void;
}

export const BacktestConfig: React.FC<BacktestConfigProps> = ({
  model,
  onBacktestComplete
}) => {
  const [form] = Form.useForm();

  const handleSubmit = async (values: any) => {
    try {
      const results = await modelService.runBacktest({
        model_config: { layers: model },
        ...values
      });
      onBacktestComplete(results);
    } catch (error) {
      console.error('Backtest failed:', error);
    }
  };

  return (
    <Form form={form} onFinish={handleSubmit} layout="vertical">
      <Form.Item label="交易对" name="symbol" rules={[{ required: true }]}>
        <Select>
          <Select.Option value="BTCUSDT">BTCUSDT</Select.Option>
          <Select.Option value="ETHUSDT">ETHUSDT</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item label="时间间隔" name="interval" rules={[{ required: true }]}>
        <Select>
          <Select.Option value="1m">1分钟</Select.Option>
          <Select.Option value="5m">5分钟</Select.Option>
          <Select.Option value="15m">15分钟</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item label="回测周期" name="period" rules={[{ required: true }]}>
        <DatePicker.RangePicker showTime />
      </Form.Item>

      <Form.Item label="初始资金" name="initial_capital" rules={[{ required: true }]}>
        <InputNumber min={1000} step={1000} style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item label="仓位大小" name="position_size" rules={[{ required: true }]}>
        <InputNumber min={0.1} max={1} step={0.1} style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item label="止损比例" name="stop_loss" rules={[{ required: true }]}>
        <InputNumber min={0.01} max={0.1} step={0.01} style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item label="止盈比例" name="take_profit" rules={[{ required: true }]}>
        <InputNumber min={0.01} max={0.2} step={0.01} style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" block>
          开始回测
        </Button>
      </Form.Item>
    </Form>
  );
}; 