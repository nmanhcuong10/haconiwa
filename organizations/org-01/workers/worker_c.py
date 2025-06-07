import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './src/components/Card';

const worker_c: React.FC = () => {
  return (
    <div className="bg-white dark:bg-gray-800 flex justify-center">
      <div className="w-full max-w-2xl p-4">
        <Card className="w-full bg-card">
          <CardHeader className="bg-card">
            <CardTitle className="text-lg font-semibold bg-card">Worker C: QA/テスト専門エージェント</CardTitle>
            <CardDescription className="text-sm text-gray-500 dark:text-gray-400 bg-card">
              自動テスト設計、実行、結果検証を行うQA/テスト専門のWorkerエージェントです。
            </CardDescription>
          </CardHeader>
          <CardContent className="bg-card">
            <div className="mb-4">
              <h3 className="text-md font-semibold mb-2">主な機能</h3>
              <ul className="list-disc pl-5">
                <li>自動テストの設計・実行・結果検証</li>
                <li>品質保証とバグレポートの作成</li>
                <li>Bossからの指示に基づくテスト戦略の実装</li>
                <li>パフォーマンステスト・セキュリティテストへの対応</li>
                <li>CI/CDパイプラインとの統合</li>
                <li>テストデータ管理と環境構築</li>
              </ul>
            </div>
            <div className="mb-4">
              <h3 className="text-md font-semibold mb-2">得意分野</h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                品質保証、テスト自動化、CI/CD連携
              </p>
            </div>
            <div>
              <h3 className="text-md font-semibold mb-2">技術スタック</h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Python, pytest, Selenium, Jenkins, JUnit
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default worker_c;
