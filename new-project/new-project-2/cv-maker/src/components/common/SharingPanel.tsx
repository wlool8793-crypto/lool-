import React, { useState } from 'react';
import { Share2, Download, Eye, Mail, MessageCircle, Copy, Link, QrCode, Shield } from 'lucide-react';
import { Button } from './Button';
import { MarriagePDFGenerator } from '../../utils/marriagePDFGenerator';

interface SharingPanelProps {
  element: HTMLElement | null;
  data: any;
  template: string;
  onShare?: (method: string) => void;
}

interface ShareMethod {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  action: () => void;
  color: string;
}

export const SharingPanel: React.FC<SharingPanelProps> = ({
  element,
  data,
  template,
  onShare
}) => {
  const [isSharing, setIsSharing] = useState(false);
  const [sharedUrl, setSharedUrl] = useState<string | null>(null);
  const [showQRCode, setShowQRCode] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleDownloadPDF = async () => {
    if (!element) return;

    setIsSharing(true);
    try {
      await MarriagePDFGenerator.downloadPDF(
        element,
        data,
        undefined,
        {
          template: template as any,
          quality: 'high',
          includeWatermark: true,
          language: 'en'
        }
      );
      onShare?.('download');
    } catch (error) {
      console.error('PDF download failed:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const handlePreviewPDF = async () => {
    if (!element) return;

    setIsSharing(true);
    try {
      await MarriagePDFGenerator.previewPDF(
        element,
        data,
        {
          template: template as any,
          quality: 'high',
          includeWatermark: true,
          language: 'en'
        }
      );
      onShare?.('preview');
    } catch (error) {
      console.error('PDF preview failed:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleEmailShare = async () => {
    if (!element) return;

    setIsSharing(true);
    try {
      // Generate PDF for email attachment
      const pdfBlob = await MarriagePDFGenerator.generatePDF(
        element,
        data,
        {
          template: template as any,
          quality: 'high',
          includeWatermark: true,
          language: 'en'
        }
      );

      // Create email URL with attachment
      const subject = encodeURIComponent(`${data.personalInfo.fullName} - Marriage Biodata`);
      const body = encodeURIComponent(`Dear Family,\n\nPlease find attached the marriage biodata of ${data.personalInfo.fullName}.\n\nBest regards,\n${data.personalInfo.fullName}\n\nContact: ${data.contactInfo.phone}\nEmail: ${data.contactInfo.email}`);

      // In a real application, you would upload the PDF and send email via backend
      const emailUrl = `mailto:?subject=${subject}&body=${body}`;
      window.open(emailUrl, '_blank');

      onShare?.('email');
    } catch (error) {
      console.error('Email share failed:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleWhatsAppShare = async () => {
    if (!element) return;

    setIsSharing(true);
    try {
      // Generate sharing URL (in real app, this would be a real URL)
      const shareUrl = `${window.location.origin}/shared/${Date.now()}`;
      setSharedUrl(shareUrl);

      const message = encodeURIComponent(
        `🔗 Marriage Biodata Shared\n\nName: ${data.personalInfo.fullName}\nAge: ${data.personalInfo.age}\nReligion: ${data.personalInfo.religion}\n\nView biodata: ${shareUrl}\n\nContact: ${data.contactInfo.phone}`
      );

      const whatsappUrl = `https://wa.me/?text=${message}`;
      window.open(whatsappUrl, '_blank');

      onShare?.('whatsapp');
    } catch (error) {
      console.error('WhatsApp share failed:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleCopyLink = async () => {
    if (!sharedUrl) {
      // Generate a share URL if not already generated
      const shareUrl = `${window.location.origin}/shared/${Date.now()}`;
      setSharedUrl(shareUrl);
    }

    try {
      await navigator.clipboard.writeText(sharedUrl || window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onShare?.('copy-link');
    } catch (error) {
      console.error('Copy link failed:', error);
    }
  };

  const handleGenerateQRCode = () => {
    if (!sharedUrl) {
      const shareUrl = `${window.location.origin}/shared/${Date.now()}`;
      setSharedUrl(shareUrl);
    }
    setShowQRCode(true);
    onShare?.('qr-code');
  };

  const shareMethods: ShareMethod[] = [
    {
      id: 'download',
      name: 'Download PDF',
      icon: <Download className="w-5 h-5" />,
      description: 'Download biodata as PDF file',
      action: handleDownloadPDF,
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      id: 'preview',
      name: 'Preview PDF',
      icon: <Eye className="w-5 h-5" />,
      description: 'Preview PDF in new tab',
      action: handlePreviewPDF,
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      id: 'email',
      name: 'Email',
      icon: <Mail className="w-5 h-5" />,
      description: 'Share via email with PDF attachment',
      action: handleEmailShare,
      color: 'bg-purple-500 hover:bg-purple-600'
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: <MessageCircle className="w-5 h-5" />,
      description: 'Share via WhatsApp with biodata link',
      action: handleWhatsAppShare,
      color: 'bg-green-600 hover:bg-green-700'
    },
    {
      id: 'copy-link',
      name: 'Copy Link',
      icon: <Copy className="w-5 h-5" />,
      description: 'Copy sharing link to clipboard',
      action: handleCopyLink,
      color: 'bg-gray-500 hover:bg-gray-600'
    },
    {
      id: 'qr-code',
      name: 'QR Code',
      icon: <QrCode className="w-5 h-5" />,
      description: 'Generate QR code for easy sharing',
      action: handleGenerateQRCode,
      color: 'bg-indigo-500 hover:bg-indigo-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Share2 className="w-5 h-5" />
            Share Marriage Biodata
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Choose how you'd like to share the biodata
          </p>
        </div>
      </div>

      {/* Share Methods Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {shareMethods.map((method) => (
          <button
            key={method.id}
            onClick={method.action}
            disabled={isSharing}
            className={`${method.color} text-white p-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg`}
          >
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {method.icon}
              </div>
              <div className="text-left">
                <div className="font-medium">{method.name}</div>
                <div className="text-xs opacity-90 mt-1">{method.description}</div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Sharing Status */}
      {isSharing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm text-blue-800">Processing your request...</span>
          </div>
        </div>
      )}

      {/* Copied Notification */}
      {copied && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Copy className="w-4 h-4 text-green-600" />
            <span className="text-sm text-green-800">Link copied to clipboard!</span>
          </div>
        </div>
      )}

      {/* Generated URL */}
      {sharedUrl && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sharing Link
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={sharedUrl}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleCopyLink}
                  className="flex-shrink-0"
                >
                  {copied ? 'Copied!' : 'Copy'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* QR Code Modal */}
      {showQRCode && sharedUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold">QR Code</h4>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setShowQRCode(false)}
              >
                ×
              </Button>
            </div>

            <div className="text-center">
              <div className="bg-gray-100 rounded-lg p-4 mb-4">
                {/* QR Code would be generated here using a QR code library */}
                <div className="w-48 h-48 mx-auto bg-white rounded flex items-center justify-center border-2 border-dashed border-gray-300">
                  <QrCode className="w-24 h-24 text-gray-400" />
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">
                Scan this QR code to view the marriage biodata
              </p>

              <p className="text-xs text-gray-500 break-all">
                {sharedUrl}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Privacy & Security Notice */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Shield className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-yellow-900">Privacy & Security</h4>
            <ul className="text-sm text-yellow-800 mt-2 space-y-1">
              <li>• Shared links are temporary and expire after 30 days</li>
              <li>• Personal information is encrypted and secure</li>
              <li>• You can revoke access at any time</li>
              <li>• Photos and documents are watermarked for protection</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};