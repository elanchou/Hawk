import React, { useState } from 'react';
import { Card, Row, Col, Tabs } from 'antd';
import { ModelConfig } from './ModelConfig';
import { BacktestConfig } from './BacktestConfig';
import { BacktestResults } from './BacktestResults';
import type { ModelLayer, BacktestResult } from '../../types';

const { TabPane } = Tabs;

export const ModelConfigPanel: React.FC = () => {
  const [currentModel, setCurrentModel] = useState<ModelLayer[]>([]);
  const [backtestResults, setBacktestResults] = useState<BacktestResult | null>(null);

  return (
    <Row gutter={[16, 16]}>
      <Col span={24}>
        <Card>
          <Tabs defaultActiveKey="model">
            <TabPane tab="模型配置" key="model">
              <ModelConfig 
                value={currentModel}
                onChange={setCurrentModel}
              />
            </TabPane>
            <TabPane tab="回测配置" key="backtest">
              <BacktestConfig 
                model={currentModel}
                onBacktestComplete={setBacktestResults}
              />
            </TabPane>
            <TabPane tab="回测结果" key="results">
              <BacktestResults results={backtestResults} />
            </TabPane>
          </Tabs>
        </Card>
      </Col>
    </Row>
  );
}; 