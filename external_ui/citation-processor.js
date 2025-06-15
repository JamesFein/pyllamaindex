/**
 * 引用处理器 - 处理API响应中的引用数据
 */
class CitationProcessor {
  constructor() {
    this.citationData = {};
  }

  /**
   * 处理API响应，提取引用数据并替换引用标记
   * @param {string} responseText - API原始响应文本
   * @returns {object} 处理后的结果
   */
  processResponse(responseText) {
    try {
      // 提取引用数据
      const citationMatch = responseText.match(
        /<!-- CITATION_DATA: (.*?) -->/s
      );
      if (citationMatch) {
        let citationJsonStr = citationMatch[1];
        try {
          // 尝试直接解析
          this.citationData = JSON.parse(citationJsonStr);
          console.log("解析到引用数据:", this.citationData);
        } catch (e) {
          console.warn("直接解析失败，尝试修复JSON:", e);
          try {
            // 修复双重转义的JSON
            const fixedJsonStr = citationJsonStr
              .replace(/\\n/g, " ")
              .replace(/\\r/g, "")
              .replace(/\\"/g, '"');
            this.citationData = JSON.parse(fixedJsonStr);
            console.log("修复后解析成功:", this.citationData);
          } catch (e2) {
            console.error("修复后仍然解析失败:", e2);
            this.citationData = {};
          }
        }
      } else {
        this.citationData = {};
      }

      // 移除引用数据注释，获取纯文本
      const cleanText = responseText
        .replace(/<!-- CITATION_DATA:.*?-->/s, "")
        .trim();

      // 处理引用标记
      const processedText = this.replaceSourceReferences(cleanText);

      return {
        text: processedText,
        citations: this.citationData,
        hasCitations: Object.keys(this.citationData).length > 0,
      };
    } catch (error) {
      console.error("处理响应时出错:", error);
      return {
        text: responseText,
        citations: {},
        hasCitations: false,
      };
    }
  }

  /**
   * 处理流式文本和引用数据（新方法）
   * @param {string} text - 纯文本
   * @param {object} citations - 引用数据对象
   * @returns {string} 处理后的HTML文本
   */
  processTextWithCitations(text, citations) {
    try {
      this.citationData = citations || {};
      console.log("处理流式文本，引用数据:", this.citationData);

      // 处理引用标记
      const processedText = this.replaceSourceReferences(text);

      return processedText;
    } catch (error) {
      console.error("处理流式文本时出错:", error);
      return this.escapeHtml(text);
    }
  }

  /**
   * 替换文本中的Source引用为可点击的引用数字
   * @param {string} text - 原始文本
   * @returns {string} 处理后的HTML文本
   */
  replaceSourceReferences(text) {
    // 查找所有的引用模式：Source 数字: 和 [数字]
    const sourcePattern = /Source (\d+):/g;
    const bracketPattern = /\[(\d+)\]/g;
    let match;
    const sourceNumbers = [];

    // 查找 Source 数字: 格式
    while ((match = sourcePattern.exec(text)) !== null) {
      sourceNumbers.push(parseInt(match[1]));
    }

    // 查找 [数字] 格式
    while ((match = bracketPattern.exec(text)) !== null) {
      sourceNumbers.push(parseInt(match[1]));
    }

    if (sourceNumbers.length === 0) {
      return this.escapeHtml(text);
    }

    // 为每个引用创建映射
    const citationMap = this.createCitationMap();

    // 替换引用为引用数字
    let processedText = text;

    // 去重
    const uniqueNumbers = [...new Set(sourceNumbers)];

    uniqueNumbers.forEach((sourceNum) => {
      const citationInfo = citationMap[sourceNum];
      if (citationInfo) {
        const citationHtml = this.createCitationHtml(sourceNum, citationInfo);

        // 替换 Source 数字: 格式
        const sourceRegex = new RegExp(`Source ${sourceNum}:`, "g");
        processedText = processedText.replace(sourceRegex, citationHtml);

        // 替换 [数字] 格式
        const bracketRegex = new RegExp(`\\[${sourceNum}\\]`, "g");
        processedText = processedText.replace(bracketRegex, citationHtml);
      }
    });

    return this.escapeHtmlExceptCitations(processedText);
  }

  /**
   * 转义HTML但保留引用标记
   * @param {string} text - 包含引用标记的文本
   * @returns {string} 转义后的文本
   */
  escapeHtmlExceptCitations(text) {
    // 先提取所有引用标记
    const citationPattern = /<span class="citation-number"[^>]*>.*?<\/span>/g;
    const citations = [];
    let match;

    while ((match = citationPattern.exec(text)) !== null) {
      citations.push(match[0]);
    }

    // 用占位符替换引用标记
    let textWithPlaceholders = text;
    citations.forEach((citation, index) => {
      textWithPlaceholders = textWithPlaceholders.replace(
        citation,
        `__CITATION_${index}__`
      );
    });

    // 转义HTML
    const escapedText = this.escapeHtml(textWithPlaceholders);

    // 恢复引用标记
    let finalText = escapedText;
    citations.forEach((citation, index) => {
      finalText = finalText.replace(`__CITATION_${index}__`, citation);
    });

    return finalText;
  }

  /**
   * 创建引用映射（按rank排序）
   * @returns {object} 引用映射
   */
  createCitationMap() {
    const citationMap = {};

    // 按rank排序引用数据
    const sortedCitations = Object.entries(this.citationData).sort(
      ([, a], [, b]) => a.rank - b.rank
    );

    sortedCitations.forEach(([nodeId, citation]) => {
      citationMap[citation.rank] = {
        nodeId,
        ...citation,
      };
    });

    return citationMap;
  }

  /**
   * 创建引用HTML
   * @param {number} rank - 引用排序
   * @param {object} citation - 引用数据
   * @returns {string} 引用HTML
   */
  createCitationHtml(rank, citation) {
    const citationData = JSON.stringify(citation).replace(/"/g, "&quot;");
    return `<span class="citation-number"
                      data-rank="${rank}"
                      data-citation="${citationData}"
                      onmouseenter="window.showCitationTooltip(event, ${rank})"
                      onmouseleave="window.hideCitationTooltip()">${rank}</span>`;
  }

  /**
   * 转义HTML特殊字符
   * @param {string} text - 原始文本
   * @returns {string} 转义后的文本
   */
  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * 获取引用数据
   * @param {number} rank - 引用排序
   * @returns {object|null} 引用数据
   */
  getCitationByRank(rank) {
    const citation = Object.values(this.citationData).find(
      (c) => c.rank === rank
    );
    return citation || null;
  }

  /**
   * 格式化文档名称
   * @param {string} filename - 原始文件名
   * @returns {string} 格式化后的文件名
   */
  formatFilename(filename) {
    return filename.replace(/^常见问题类-\d+_/, "").replace(/\.txt$/, "");
  }

  /**
   * 格式化相似度分数
   * @param {number} score - 相似度分数
   * @returns {string} 格式化后的分数
   */
  formatSimilarityScore(score) {
    return Math.round(score * 100) + "%";
  }
}

// 全局引用处理器实例
window.citationProcessor = new CitationProcessor();

// 全局引用悬浮框函数
window.showCitationTooltip = function (event, rank) {
  const citation = window.citationProcessor.getCitationByRank(rank);
  if (!citation) return;

  // 创建或获取悬浮框元素
  let tooltip = document.getElementById("citation-tooltip");
  if (!tooltip) {
    tooltip = document.createElement("div");
    tooltip.id = "citation-tooltip";
    tooltip.className = "citation-tooltip";
    document.body.appendChild(tooltip);
  }

  // 格式化文档名和相似度
  const formattedFilename = window.citationProcessor.formatFilename(
    citation.filename
  );
  const formattedSimilarity = window.citationProcessor.formatSimilarityScore(
    citation.similarity_score
  );

  // 设置悬浮框内容
  tooltip.innerHTML = `
    <div class="citation-header">引用 #${rank}</div>
    <div class="citation-filename">文档: ${formattedFilename}</div>
    <div class="citation-similarity">相似度: ${formattedSimilarity}</div>
    <div class="citation-content">${citation.content}</div>
  `;

  // 计算位置
  const rect = event.target.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();

  let left = rect.left + window.scrollX;
  let top = rect.bottom + window.scrollY + 5;

  // 防止悬浮框超出屏幕右边界
  if (left + 400 > window.innerWidth) {
    left = window.innerWidth - 400 - 10;
  }

  // 防止悬浮框超出屏幕下边界
  if (top + 300 > window.innerHeight + window.scrollY) {
    top = rect.top + window.scrollY - 300 - 5;
  }

  tooltip.style.left = left + "px";
  tooltip.style.top = top + "px";
  tooltip.style.display = "block";
};

window.hideCitationTooltip = function () {
  const tooltip = document.getElementById("citation-tooltip");
  if (tooltip) {
    tooltip.style.display = "none";
  }
};
