import React from 'react';
import { Card, Form, Input, Button, Select, InputNumber } from 'antd';
import { tradingService } from '../../services/tradingService';

const { Option } = Select;

interface TradeControlProps {
    symbol: string;
    onTrade: () => void;
}

export const TradeControl: React.FC<TradeControlProps> = ({ symbol, onTrade }) => {
    const [form] = Form.useForm();

    const handleSubmit = async (values: any) => {
        try {
            // 这里添加下单逻辑
            await tradingService.placeTrade({
                symbol: values.symbol,
                type: values.type,
                quantity: values.quantity,
                price: values.price
            });
            onTrade();
            form.resetFields();
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
                initialValues={{ symbol, type: 'market' }}
            >
                <Form.Item name="symbol" label="交易对">
                    <Input disabled />
                </Form.Item>
                
                <Form.Item name="type" label="订单类型">
                    <Select>
                        <Option value="market">市价单</Option>
                        <Option value="limit">限价单</Option>
                    </Select>
                </Form.Item>
                
                <Form.Item name="quantity" label="数量" rules={[{ required: true }]}>
                    <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
                
                <Form.Item
                    noStyle
                    shouldUpdate={(prevValues, currentValues) => prevValues.type !== currentValues.type}
                >
                    {({ getFieldValue }) => 
                        getFieldValue('type') === 'limit' ? (
                            <Form.Item name="price" label="价格" rules={[{ required: true }]}>
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
            </Form>
        </Card>
    );
}; 