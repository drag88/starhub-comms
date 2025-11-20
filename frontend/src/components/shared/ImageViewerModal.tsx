import React, { useState } from 'react';
import type { Creative } from '../../types/creative';
import { API_BASE_URL } from '../../services/api';

interface ImageViewerModalProps {
  creatives: Creative[];
  initialIndex?: number;
  isOpen: boolean;
  onClose: () => void;
}

export const ImageViewerModal: React.FC<ImageViewerModalProps> = ({
  creatives,
  initialIndex = 0,
  isOpen,
  onClose,
}) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  if (!isOpen || creatives.length === 0) return null;

  const currentCreative = creatives[currentIndex];
  const imageUrl = currentCreative.image_url.startsWith('http')
    ? currentCreative.image_url
    : `${API_BASE_URL}${currentCreative.image_url}`;

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : creatives.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < creatives.length - 1 ? prev + 1 : 0));
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = currentCreative.image_filename || `creative_${currentCreative.creative_id}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download image. Please try again.');
    }
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-6xl mx-4">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute -top-12 right-0 text-white hover:text-gray-300 text-4xl font-bold z-10"
          aria-label="Close"
        >
          ×
        </button>

        {/* Main content */}
        <div className="bg-white rounded-lg shadow-2xl overflow-hidden">
          {/* Image */}
          <div className="relative bg-gray-900">
            <img
              src={imageUrl}
              alt={`Creative variant ${currentCreative.variant_number}`}
              className="w-full h-auto max-h-[70vh] object-contain"
            />

            {/* Navigation arrows */}
            {creatives.length > 1 && (
              <>
                <button
                  onClick={handlePrevious}
                  className="absolute left-4 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-full w-12 h-12 flex items-center justify-center text-2xl transition-all"
                  aria-label="Previous image"
                >
                  ‹
                </button>
                <button
                  onClick={handleNext}
                  className="absolute right-4 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-full w-12 h-12 flex items-center justify-center text-2xl transition-all"
                  aria-label="Next image"
                >
                  ›
                </button>
              </>
            )}

            {/* Image counter */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black bg-opacity-75 text-white px-4 py-2 rounded-full text-sm">
              {currentIndex + 1} / {creatives.length}
            </div>
          </div>

          {/* Info panel */}
          <div className="p-6 bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  Variant {currentCreative.variant_number}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Channel: <span className="font-medium">{currentCreative.channel_type.replace('_', ' ')}</span>
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    {currentCreative.recommendation_score}/100
                  </div>
                  <div className="text-xs text-gray-600">Score</div>
                </div>
              </div>
            </div>

            {/* Score reasoning */}
            {currentCreative.score_reasoning && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700">{currentCreative.score_reasoning}</p>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleDownload}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Image
              </button>
              <button
                onClick={onClose}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-semibold text-gray-700"
              >
                Close
              </button>
            </div>

            {/* Keyboard shortcuts hint */}
            {creatives.length > 1 && (
              <div className="mt-4 text-center text-xs text-gray-500">
                Use ← → arrow keys or click buttons to navigate
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageViewerModal;

