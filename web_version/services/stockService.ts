
export class StockService {
  private apiKey: string;
  private baseUrl = 'https://api.unsplash.com';

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async getAggressiveImage(animal: string): Promise<string> {
    try {
      // Clean up the query (remove 'vs', underscores, etc)
      let query = animal.replace(/_/g, ' ').replace(/_vs_/g, ' fight ');
      
      // Make it aggressive
      if (!query.includes('fight')) {
        query = `angry ${query} roar attack`;
      }

      const response = await fetch(
        `${this.baseUrl}/search/photos?query=${encodeURIComponent(query)}&orientation=portrait&per_page=5&content_filter=high`, 
        {
          headers: {
            'Authorization': `Client-ID ${this.apiKey}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Unsplash API Error: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.results && data.results.length > 0) {
        // Pick a random one from the top 5 to vary it up
        const randomIndex = Math.floor(Math.random() * Math.min(data.results.length, 5));
        return data.results[randomIndex].urls.regular;
      }
      
      throw new Error("No stock images found");
    } catch (error) {
      console.warn("Stock Service Failed:", error);
      return ''; // Handle in UI
    }
  }
}
