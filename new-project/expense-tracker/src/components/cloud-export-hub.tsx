'use client';

import { useState, useEffect } from 'react';
import * as React from 'react';
import { Expense } from '@/types/expense';
import {
  CloudExportJob,
  ExportTemplate,
  ShareableLink,
} from '@/types/cloud-export';
import { cloudExportService, defaultTemplates, mockIntegrations } from '@/lib/cloud-export-utils';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import {
  Cloud,
  Share2,
  Download,
  Mail,
  Clock,
  Link,
  CheckCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
  Settings,
  FileText,
  Sheet,
  Folder,
  Database,
  Zap,
} from 'lucide-react';

interface CloudExportHubProps {
  isOpen: boolean;
  onClose: () => void;
  expenses: Expense[];
}

const formatIcons = {
  csv: FileText,
  json: Database,
  pdf: FileText,
  xlsx: Sheet,
  'google-sheet': Sheet,
};

const destinationIcons = {
  download: Download,
  email: Mail,
  'google-drive': Folder,
  dropbox: Folder,
  onedrive: Folder,
  'google-sheets': Sheet,
  webhook: Zap,
};

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
};

export function CloudExportHub({ isOpen, onClose, expenses }: CloudExportHubProps) {
  const [activeTab, setActiveTab] = useState('export');
  const [exportJobs, setExportJobs] = useState<CloudExportJob[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ExportTemplate>(defaultTemplates[0]);
  const [customRecipients, setCustomRecipients] = useState('');
  const [, setShareableLinks] = useState<ShareableLink[]>([]);
  const [qrCodeData, setQrCodeData] = useState<string>('');
  const [isCreatingExport, setIsCreatingExport] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadExportData();
    }
  }, [isOpen]);

  const loadExportData = () => {
    setExportJobs(cloudExportService.getAllExportJobs());
    setShareableLinks(cloudExportService.getShareableLinks());
  };

  const handleCreateExport = async () => {
    if (!selectedTemplate) return;

    setIsCreatingExport(true);
    try {
      const job = await cloudExportService.createExportJob(
        expenses,
        'manual',
        selectedTemplate.destination,
        selectedTemplate.format,
        selectedTemplate
      );

      // Add recipients if email export
      if (selectedTemplate.destination === 'email' && customRecipients) {
        // In a real implementation, this would update the job config
      }

      // Poll for job completion
      const interval = setInterval(() => {
        const updatedJob = cloudExportService.getExportJob(job.id);
        if (updatedJob) {
          setExportJobs(cloudExportService.getAllExportJobs());

          if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
            clearInterval(interval);
            setIsCreatingExport(false);
          }
        }
      }, 500);

      setTimeout(() => clearInterval(interval), 10000); // Safety timeout
    } catch (error) {
      console.error('Failed to create export:', error);
      setIsCreatingExport(false);
    }
  };

  const handleCreateShareableLink = async (jobId: string) => {
    try {
      const link = await cloudExportService.createShareableLink(jobId, true);
      setShareableLinks(cloudExportService.getShareableLinks());

      // Generate QR code
      const qrCode = await cloudExportService.generateQRCode(link.url);
      setQrCodeData(qrCode);
    } catch (error) {
      console.error('Failed to create shareable link:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Cloud className="h-6 w-6" />
            Cloud Export Hub
          </DialogTitle>
          <DialogDescription>
            Modern cloud-powered export system with sharing, scheduling, and integrations
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="export">Quick Export</TabsTrigger>
            <TabsTrigger value="templates">Templates</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
          </TabsList>

          <TabsContent value="export" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Export Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Export Configuration
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Select Template</Label>
                    <div className="grid grid-cols-1 gap-2 mt-2">
                      {defaultTemplates.map((template) => (
                        <div
                          key={template.id}
                          className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                            selectedTemplate.id === template.id
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => setSelectedTemplate(template)}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="flex items-center gap-2">
                                {React.createElement(
                                  formatIcons[template.format] || FileText,
                                  { className: 'h-4 w-4' }
                                )}
                                <span className="font-medium">{template.name}</span>
                              </div>
                              <p className="text-sm text-gray-600 mt-1">
                                {template.description}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              {React.createElement(
                                destinationIcons[template.destination] || Download,
                                { className: 'h-4 w-4 text-gray-500' }
                              )}
                              {selectedTemplate.id === template.id && (
                                <CheckCircle className="h-4 w-4 text-blue-500" />
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {selectedTemplate.destination === 'email' && (
                    <div>
                      <Label htmlFor="recipients">Email Recipients</Label>
                      <Input
                        id="recipients"
                        placeholder="email@example.com, another@example.com"
                        value={customRecipients}
                        onChange={(e) => setCustomRecipients(e.target.value)}
                        className="mt-1"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Separate multiple emails with commas
                      </p>
                    </div>
                  )}

                  <Button
                    onClick={handleCreateExport}
                    disabled={isCreatingExport || expenses.length === 0}
                    className="w-full"
                  >
                    {isCreatingExport ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Creating Export...
                      </>
                    ) : (
                      <>
                        <Cloud className="h-4 w-4 mr-2" />
                        Export {expenses.length} Expenses
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Active Export Jobs */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <RefreshCw className="h-5 w-5" />
                    Active Exports
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {exportJobs.filter(job => job.status === 'processing' || job.status === 'pending').length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No active exports
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {exportJobs
                        .filter(job => job.status === 'processing' || job.status === 'pending')
                        .map((job) => (
                          <div key={job.id} className="border rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                {getStatusIcon(job.status)}
                                <span className="font-medium capitalize">{job.status}</span>
                              </div>
                              <Badge variant="outline">{job.format}</Badge>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${job.progress}%` }}
                              />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              {job.progress}% complete
                            </p>
                          </div>
                        ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Recent Export Jobs */}
            {exportJobs.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Recent Export Jobs</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {exportJobs.slice(0, 5).map((job) => (
                      <div key={job.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(job.status)}
                          <div>
                            <p className="font-medium capitalize">{job.type} Export</p>
                            <p className="text-sm text-gray-500">
                              {job.destination} • {job.format}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={statusColors[job.status]}>
                            {job.status}
                          </Badge>
                          {job.status === 'completed' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCreateShareableLink(job.id)}
                            >
                              <Share2 className="h-4 w-4" />
                            </Button>
                          )}
                          {job.downloadUrl && (
                            <Button variant="outline" size="sm" asChild>
                              <a href={job.downloadUrl} target="_blank" rel="noopener noreferrer">
                                <Download className="h-4 w-4" />
                              </a>
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="templates" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {defaultTemplates.map((template) => (
                <Card key={template.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {React.createElement(
                        formatIcons[template.format] || FileText,
                        { className: 'h-5 w-5' }
                      )}
                      {template.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 mb-3">
                      {template.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">{template.format}</Badge>
                      {React.createElement(
                        destinationIcons[template.destination] || Download,
                        { className: 'h-4 w-4 text-gray-500' }
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            {exportJobs.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-gray-500">No export history yet</p>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Export History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {exportJobs.map((job) => (
                      <div key={job.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(job.status)}
                          <div>
                            <p className="font-medium capitalize">{job.type} Export</p>
                            <p className="text-sm text-gray-500">
                              {job.completedAt ? formatDate(job.completedAt) : 'In progress'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={statusColors[job.status]}>
                            {job.status}
                          </Badge>
                          {job.shareUrl && (
                            <Button variant="outline" size="sm">
                              <Link className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="integrations" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockIntegrations.map((integration) => (
                <Card key={integration.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        {React.createElement(
                          destinationIcons[integration.type] || Settings,
                          { className: 'h-5 w-5' }
                        )}
                        {integration.name}
                      </span>
                      <Badge variant={integration.isConnected ? 'default' : 'secondary'}>
                        {integration.isConnected ? 'Connected' : 'Not Connected'}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {integration.isConnected && integration.lastSync && (
                      <p className="text-sm text-gray-500 mb-3">
                        Last sync: {formatDate(integration.lastSync)}
                      </p>
                    )}
                    <Button
                      variant={integration.isConnected ? 'outline' : 'default'}
                      size="sm"
                      className="w-full"
                    >
                      {integration.isConnected ? 'Configure' : 'Connect'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* QR Code Modal */}
        {qrCodeData && (
          <Dialog open={!!qrCodeData} onOpenChange={() => setQrCodeData('')}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Share Export via QR Code</DialogTitle>
              </DialogHeader>
              <div className="text-center">
                <img src={qrCodeData} alt="QR Code" className="mx-auto mb-4" />
                <p className="text-sm text-gray-600">
                  Scan this QR code to access the shared export
                </p>
              </div>
            </DialogContent>
          </Dialog>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}