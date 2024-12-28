import React, { useState, useEffect } from 'react';
import { Card, Form, Select, InputNumber, Button, Space } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import { modelService } from '../../services/modelService';

export const ModelConfig: React.FC = () => {
  const [layerTypes, setLayerTypes] = useState<any>({});
  const [form] = Form.useForm();

  useEffect(() => {
    modelService.getLayerTypes().then(setLayerTypes);
    modelService.getModelConfig().then(config => form.setFieldsValue(config));
  }, []);

  const handleSubmit = async (values: any) => {
    try {
      await modelService.updateModelConfig(values);
    } catch (error) {
      console.error('Failed to update model config:', error);
    }
  };

  return (
    <Card title="模型配置">
      <Form form={form} onFinish={handleSubmit}>
        <Form.List name="layers">
          {(fields, { add, remove }) => (
            <>
              {fields.map((field, index) => (
                <Space key={field.key} align="baseline">
                  <Form.Item
                    {...field}
                    label={`层 ${index + 1}`}
                    required
                  >
                    <Select
                      style={{ width: 200 }}
                      onChange={(type) => {
                        // 重置该层的参数
                        const params = layerTypes[type].params;
                        form.setFieldsValue({
                          layers: {
                            [index]: { type, ...params }
                          }
                        });
                      }}
                    >
                      {Object.keys(layerTypes).map(type => (
                        <Select.Option key={type} value={type}>
                          {type}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                  <MinusCircleOutlined onClick={() => remove(field.name)} />
                </Space>
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
        <Form.Item>
          <Button type="primary" htmlType="submit">
            保存配置
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
}; 