import React from 'react';
import { Form, Select, InputNumber, Button, Space, Divider } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import type { ModelLayer, LayerType } from '../../types';

interface ModelConfigProps {
  value: ModelLayer[];
  onChange: (layers: ModelLayer[]) => void;
}

const LAYER_TYPES: Record<LayerType, any> = {
  linear: {
    name: '线性层',
    params: {
      output_size: { type: 'number', label: '输出维度', min: 1 },
      activation: { 
        type: 'select', 
        label: '激活函数',
        options: ['ReLU', 'Tanh', 'GELU']
      },
      dropout: { type: 'number', label: '丢弃率', min: 0, max: 1, step: 0.1 }
    }
  },
  lstm: {
    name: 'LSTM层',
    params: {
      hidden_size: { type: 'number', label: '隐藏维度', min: 1 },
      num_layers: { type: 'number', label: '层数', min: 1 },
      dropout: { type: 'number', label: '丢弃率', min: 0, max: 1, step: 0.1 },
      bidirectional: { type: 'boolean', label: '双向' }
    }
  },
  gru: {
    name: 'GRU层',
    params: {
      hidden_size: { type: 'number', label: '隐藏维度', min: 1 },
      num_layers: { type: 'number', label: '层数', min: 1 },
      dropout: { type: 'number', label: '丢弃率', min: 0, max: 1, step: 0.1 },
      bidirectional: { type: 'boolean', label: '双向' }
    }
  },
  attention: {
    name: '注意力层',
    params: {
      hidden_size: { type: 'number', label: '隐藏维度', min: 1 },
      num_heads: { type: 'number', label: '注意力头数', min: 1 },
      dropout: { type: 'number', label: '丢弃率', min: 0, max: 1, step: 0.1 }
    }
  },
  tcn: {
    name: '时间卷积层',
    params: {
      hidden_size: { type: 'number', label: '隐藏维度', min: 1 },
      kernel_size: { type: 'number', label: '卷积核大小', min: 1, step: 2 },
      dilation: { type: 'number', label: '扩张率', min: 1 },
      dropout: { type: 'number', label: '丢弃率', min: 0, max: 1, step: 0.1 }
    }
  },
  transformer: {
    name: 'Transformer层',
    params: {
      hidden_size: { type: 'number', label: '隐藏维度', min: 1 },
      num_heads: { type: 'number', label: '注意力头数', min: 1 },
      dropout: { type: 'number', label: '丢弃率', min: 0, max: 1, step: 0.1 }
    }
  }
};

export const ModelConfig: React.FC<ModelConfigProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();

  const handleValuesChange = () => {
    const values = form.getFieldsValue();
    onChange(values.layers || []);
  };

  return (
    <Form 
      form={form}
      initialValues={{ layers: value }}
      onValuesChange={handleValuesChange}
    >
      <Form.List name="layers">
        {(fields, { add, remove, move }) => (
          <>
            {fields.map((field, index) => (
              <div key={field.key}>
                <Divider>{`层 ${index + 1}`}</Divider>
                <Space align="baseline">
                  <Form.Item
                    {...field}
                    label="类型"
                    name={[field.name, 'type']}
                    rules={[{ required: true }]}
                  >
                    <Select style={{ width: 200 }}>
                      {Object.entries(LAYER_TYPES).map(([type, config]) => (
                        <Select.Option key={type} value={type}>
                          {config.name}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                  
                  <Form.Item shouldUpdate noStyle>
                    {() => {
                      const type = form.getFieldValue(['layers', index, 'type']);
                      const config = LAYER_TYPES[type as LayerType];
                      
                      if (!config) return null;
                      
                      return Object.entries(config.params).map(([key, param]: [string, any]) => (
                        <Form.Item
                          key={key}
                          label={param.label}
                          name={[field.name, key]}
                          rules={[{ required: true }]}
                        >
                          {param.type === 'select' ? (
                            <Select style={{ width: 120 }}>
                              {param.options.map((opt: string) => (
                                <Select.Option key={opt} value={opt}>
                                  {opt}
                                </Select.Option>
                              ))}
                            </Select>
                          ) : (
                            <InputNumber
                              style={{ width: 120 }}
                              min={param.min}
                              max={param.max}
                              step={param.step}
                            />
                          )}
                        </Form.Item>
                      ));
                    }}
                  </Form.Item>
                  
                  <MinusCircleOutlined onClick={() => remove(field.name)} />
                </Space>
              </div>
            ))}
            
            <Form.Item>
              <Button 
                type="dashed" 
                onClick={() => add()} 
                block 
                icon={<PlusOutlined />}
              >
                添加层
              </Button>
            </Form.Item>
          </>
        )}
      </Form.List>
    </Form>
  );
}; 