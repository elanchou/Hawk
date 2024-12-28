import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Progress, Statistic } from 'antd';
import { Line } from '@ant-design/charts';

export const TrainingMonitor: React.FC = () => {
  const [trainingStats, setTrainingStats] = useState<any>({});
  const [lossHistory, setLossHistory] = useState<any[]>([]);

  useEffect(() => {
    // 实现WebSocket连接以获取实时训练状态
  }, []);

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="当前Epoch" value={trainingStats.currentEpoch} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="训练损失" value={trainingStats.trainLoss} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="验证损失" value={trainingStats.valLoss} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Progress 
              type="circle" 
              percent={trainingStats.progress} 
              status="active"
            />
          </Card>
        </Col>
      </Row>

      <Card title="损失曲线" style={{ marginTop: 16 }}>
        <Line
          data={lossHistory}
          xField="epoch"
          yField="value"
          seriesField="type"
        />
      </Card>
    </div>
  );
}; 