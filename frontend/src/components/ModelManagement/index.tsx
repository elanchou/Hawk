import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Upload, message, Modal } from 'antd';
import { UploadOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { modelService } from '../../services/modelService';

export const ModelManagement: React.FC = () => {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await modelService.listModels();
      setModels(response.models);
    } catch (error) {
      message.error('加载模型列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  const columns = [
    {
      title: '模型名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: '操作',
      key: 'action',
      render: (text: string, record: any) => (
        <Button.Group>
          <Button 
            icon={<PlayCircleOutlined />}
            onClick={() => {/* 启动训练 */}}
          >
            训练
          </Button>
          <Button 
            icon={<DeleteOutlined />}
            danger
            onClick={() => {/* 删除模型 */}}
          >
            删除
          </Button>
        </Button.Group>
      ),
    },
  ];

  return (
    <Card 
      title="模型管理" 
      extra={
        <Upload 
          accept=".pth,.pt"
          beforeUpload={async (file) => {
            try {
              await modelService.uploadModel(file);
              message.success('模型上传成功');
              loadModels();
            } catch (error) {
              message.error('模型上传失败');
            }
            return false;
          }}
        >
          <Button icon={<UploadOutlined />}>上传模型</Button>
        </Upload>
      }
    >
      <Table 
        columns={columns}
        dataSource={models}
        loading={loading}
        rowKey="id"
      />
    </Card>
  );
}; 