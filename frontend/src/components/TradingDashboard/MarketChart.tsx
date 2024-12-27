import React from 'react';
import {
    createChart,
    ColorType,
    CrosshairMode,
    IChartApi,
    ISeriesApi,
    Time
} from 'lightweight-charts';
import { Card } from 'antd';
import styled from '@emotion/styled';

const ChartContainer = styled.div`
    width: 100%;
    height: 500px;
`;

interface MarketData {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

interface MarketChartProps {
    data: MarketData[];
    indicators: any[];
}

export const MarketChart: React.FC<MarketChartProps> = ({ data, indicators }) => {
    const chartContainerRef = React.useRef<HTMLDivElement>(null);
    const [chart, setChart] = React.useState<IChartApi | null>(null);
    const [candleSeries, setCandleSeries] = React.useState<ISeriesApi<"Candlestick"> | null>(null);

    React.useEffect(() => {
        if (chartContainerRef.current) {
            const chartInstance = createChart(chartContainerRef.current, {
                width: chartContainerRef.current.clientWidth,
                height: 500,
                layout: {
                    background: { color: '#ffffff' },
                    textColor: '#333',
                },
                grid: {
                    vertLines: { color: '#f0f0f0' },
                    horzLines: { color: '#f0f0f0' },
                },
                crosshair: {
                    mode: CrosshairMode.Normal,
                },
                rightPriceScale: {
                    borderColor: '#f0f0f0',
                },
                timeScale: {
                    borderColor: '#f0f0f0',
                    timeVisible: true,
                },
            });

            const candleStickSeries = chartInstance.addCandlestickSeries({
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderVisible: false,
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
            });

            setChart(chartInstance);
            setCandleSeries(candleStickSeries);

            const handleResize = () => {
                if (chartContainerRef.current) {
                    chartInstance.applyOptions({
                        width: chartContainerRef.current.clientWidth,
                    });
                }
            };

            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);
                chartInstance.remove();
            };
        }
    }, []);

    React.useEffect(() => {
        if (candleSeries && data.length > 0) {
            const formattedData = data.map(d => ({
                time: d.timestamp as Time,
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close,
            }));
            candleSeries.setData(formattedData);
        }
    }, [candleSeries, data]);

    return (
        <Card title="市场行情">
            <ChartContainer ref={chartContainerRef} />
        </Card>
    );
}; 