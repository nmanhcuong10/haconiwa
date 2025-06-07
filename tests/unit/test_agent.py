import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '.src/components/ui/card';

const test_agent: React.FC = () => {
  return (
    <div className="flex justify-center bg-white dark:bg-gray-800">
      <div className="w-full max-w-2xl p-4 bg-white dark:bg-gray-800">
        <Card className="w-full bg-card">
          <CardHeader className="bg-card">
            <CardTitle className="text-lg font-semibold bg-card">haconiwa agent モジュール ユニットテスト</CardTitle>
            <CardDescription className="text-sm text-muted-foreground bg-card">
              pytest フレームワークを使用したテストケース
            </CardDescription>
          </CardHeader>
          <CardContent className="bg-card">
            <ul className="list-disc pl-5">
              <li>base.py の基底エージェントクラステスト</li>
              <li>boss.py のBossエージェント機能テスト</li>
              <li>worker.py のWorkerエージェント機能テスト</li>
              <li>manager.py のManagerエージェント機能テスト</li>
              <li>エージェント間通信のテスト</li>
              <li>タスク割り当て・実行のテスト</li>
              <li>AIモデル連携のモックテスト</li>
            </ul>
            <div className="mt-4">
              <p className="text-sm text-gray-500 dark:text-gray-400 bg-card">
                依存関係:
              </p>
              <ul className="list-disc pl-5 text-sm text-gray-500 dark:text-gray-400">
                <li>src/haconiwa/agent/base.py</li>
                <li>src/haconiwa/agent/boss.py</li>
                <li>src/haconiwa/agent/worker.py</li>
                <li>src/haconiwa/agent/manager.py</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default test_agent;