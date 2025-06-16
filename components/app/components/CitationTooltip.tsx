"use client";

import { useState, useRef, useEffect } from "react";
import { LoadingSpinner } from "./LoadingSpinner";

interface CitationData {
  id: string;
  title: string;
  content: string;
  metadata?: {
    file_name?: string;
    [key: string]: any;
  };
}

interface CitationTooltipProps {
  citationId: string;
  children: React.ReactNode;
}

export function CitationTooltip({
  citationId,
  children,
}: CitationTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [citationData, setCitationData] = useState<CitationData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLSpanElement>(null);

  const loadCitationData = async () => {
    if (citationData || isLoading) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/citation/${citationId}`);
      if (!response.ok) throw new Error("Failed to load citation");

      const data = await response.json();
      setCitationData({
        id: data.id || citationId,
        title:
          data.metadata?.file_name ||
          `Document ${citationId.substring(0, 8)}...`,
        content: data.text || data.content || "内容不可用",
        metadata: data.metadata,
      });
    } catch (error) {
      console.error("Error loading citation:", error);
      setCitationData({
        id: citationId,
        title: "Error",
        content: "Failed to load citation content",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleMouseEnter = (e: React.MouseEvent) => {
    const rect = triggerRef.current?.getBoundingClientRect();
    if (rect) {
      setPosition({
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
      });
    }
    setIsVisible(true);
    loadCitationData();
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  useEffect(() => {
    if (isVisible && tooltipRef.current) {
      const tooltip = tooltipRef.current;
      const rect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let adjustedX = position.x - rect.width / 2;
      let adjustedY = position.y - rect.height;

      // 确保tooltip不超出视口
      if (adjustedX < 10) adjustedX = 10;
      if (adjustedX + rect.width > viewportWidth - 10) {
        adjustedX = viewportWidth - rect.width - 10;
      }
      if (adjustedY < 10) adjustedY = position.y + 30;

      tooltip.style.left = `${adjustedX}px`;
      tooltip.style.top = `${adjustedY}px`;
    }
  }, [isVisible, position.x, position.y, citationData]);

  return (
    <>
      <span
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="citation-number"
      >
        {children}
      </span>

      {isVisible && (
        <div
          ref={tooltipRef}
          className="citation-tooltip fixed z-50"
          style={{ left: position.x, top: position.y }}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <LoadingSpinner size="sm" className="text-blue-600" />
              <span>Loading...</span>
            </div>
          ) : citationData ? (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {citationData.title}
              </h4>
              <div className="text-gray-700 text-sm leading-relaxed">
                {citationData.content.length > 300
                  ? `${citationData.content.substring(0, 300)}...`
                  : citationData.content}
              </div>
            </div>
          ) : (
            <div>Error loading citation</div>
          )}
        </div>
      )}
    </>
  );
}
