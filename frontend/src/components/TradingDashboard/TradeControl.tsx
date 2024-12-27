import React from 'react';
import { Card, Form, Input, Button, Select, InputNumber, Space } from 'antd';
import { tradingService } from '../../services/tradingService';

const { Option } = Select;

interface TradeControlProps {
  symbol: string;
  exchange: string;
  onTrade: () => void;
}

export const TradeControl: React.FC<TradeControlProps> = ({ 
  symbol, 
  exchange, 
  onTrade 
}) => {
  const [form] = Form.useForm();

  const handleSubmit = async (values: any) => {
    try {
      await tradingService.placeTrade({
        symbol,
        type: values.type,
        side: values.side,
        quantity: values.quantity,
        price: values.type === 'limit' ? values.price : undefined
      });
      onTrade();
      form.resetFields(['quantity', 'price']);
    } catch (error) {
      console.error('Trade failed:', error);
    }
  };

  return (
    <Card title="交易控制">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{ type: 'market', side: 'buy' }}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Form.Item name="side" label="交易方向">
            <Select>
              <Option value="buy">买入</Option>
              <Option value="sell">卖出</Option>
            </Select>
          </Form.Item>

          <Form.Item name="type" label="订单类型">
            <Select>
              <Option value="market">市价单</Option>
              <Option value="limit">限价单</Option>
            </Select>
          </Form.Item>

          <Form.Item 
            name="quantity" 
            label="数量"
            rules={[{ required: true, message: '请输入数量' }]}
          >
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => 
              prevValues.type !== currentValues.type
            }
          >
            {({ getFieldValue }) => 
              getFieldValue('type') === 'limit' ? (
                <Form.Item
                  name="price"
                  label="价格"
                  rules={[{ required: true, message: '请输入价格' }]}
                >
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              下单
            </Button>
          </Form.Item>
        </Space>
      </Form>
    </Card>
  );
}; 