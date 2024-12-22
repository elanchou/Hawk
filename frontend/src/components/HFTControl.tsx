import React, { useState } from 'react';
import { Card, Form, InputNumber, Switch, Button, Space, Statistic } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import { tradingService } from '../services/tradingService';

interface HFTControlProps {
  symbol: string;
  exchange: string;
}

export const HFTControl: React.FC<HFTControlProps> = ({ symbol, exchange }) => {
  const [running, setRunning] = useState(false);
  const [form] = Form.useForm();

  const handleStart = async () => {
    try {
      const values = await form.validateFields();
      await tradingService.startHFT({
        symbol,
        exchange,
        ...values
      });
      setRunning(true);
    } catch (error) {
      console.error('Failed to start HFT:', error);
    }
  };

  const handleStop = async () => {
    try {
      await tradingService.stopHFT(symbol);
      setRunning(false);
    } catch (error) {
      console.error('Failed to stop HFT:', error);
    }
  };

  return (
    <Card title="高频交易控制" extra={
      <Switch
        checked={running}
        onChange={(checked) => checked ? handleStart() : handleStop()}
        checkedChildren={<PlayCircleOutlined />}
        unCheckedChildren={<PauseCircleOutlined />}
      />
    }>
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          tick_interval: 0.1,
          position_limit: 0.1,
          min_spread: 0.0002,
          min_profit: 0.0001
        }}
      >
        <Form.Item
          name="tick_interval"
          label="Tick间隔(秒)"
          rules={[{ required: true }]}
        >
          <InputNumber min={0.01} step={0.01} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="position_limit"
          label="仓位限制"
          rules={[{ required: true }]}
        >
          <InputNumber min={0.01} max={1} step={0.01} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="min_spread"
          label="最小价差"
          rules={[{ required: true }]}
        >
          <InputNumber min={0.0001} step={0.0001} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="min_profit"
          label="最小利润"
          rules={[{ required: true }]}
        >
          <InputNumber min={0.0001} step={0.0001} style={{ width: '100%' }} />
        </Form.Item>
      </Form>

      <Space direction="vertical" style={{ width: '100%' }}>
        <Statistic title="当前持仓" value={0} />
        <Statistic title="今日交易次数" value={0} />
        <Statistic title="今日盈亏" value={0} prefix="$" precision={2} />
      </Space>
    </Card>
  );
}; 