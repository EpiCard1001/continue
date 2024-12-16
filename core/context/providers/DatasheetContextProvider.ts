import {
    ContextItem,
    ContextProviderDescription,
    ContextProviderExtras,
    ContextSubmenuItem,
    LoadSubmenuItemsArgs,
  } from "../..";
  import { BaseContextProvider } from "..";
  class DatasheetContextProvider extends BaseContextProvider {
    static description: ContextProviderDescription = {
      title: "datasheet",
      displayTitle: "Datasheets",
      description: "Use indexed Datasheets",
      type: "submenu"
    };
    async getContextItems(
      query: string,
      extras: ContextProviderExtras,
    ): Promise<ContextItem[]> {
      let results;
      const input_query = extras.fullInput;
      if (query == "0") {
        
        const response = await fetch("http://127.0.0.1:8000/retrieve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: input_query, tp: 0 }),  // Correct request body format
        });
        results = await response.json();
      }
      else if (query == "1") {
        
        const response = await fetch("http://127.0.0.1:8000/retrieve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: input_query, tp: 1 }),  // Correct request body format
        });
        results = await response.json();
      }
      return results.map((result: any) => ({
        name: result.title,
        description: result.contents,
        content: result.contents,
      }));;
    }
    async loadSubmenuItems(
      args: LoadSubmenuItemsArgs,
    ): Promise<ContextSubmenuItem[]> {
      const ts = [{ id: "0", title: "AIS328DQ", description: "AIS328DQ" }, { id: "1", title: "OVA5640", description: "OVA5640" }];
      // Return the items that will be shown in the dropdown
      return ts;
    }
  }
  export default DatasheetContextProvider;