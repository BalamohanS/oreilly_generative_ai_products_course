package org.example;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Excel to JSON Converter for Windows/IntelliJ Environment
 *
 * Dependencies required in pom.xml:
 * - Apache POI (poi, poi-ooxml)
 * - Jackson (jackson-databind)
 */
public class ExcelToJsonConverter {

    private static final ObjectMapper objectMapper;

    static {
        objectMapper = new ObjectMapper();
        objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
        objectMapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
    }

    /**
     * Main method for testing and demonstration
     */
    public static void main(String[] args) {
        System.out.println("🚀 Excel to JSON Converter - Java Edition (Windows/IntelliJ)");
        System.out.println("=".repeat(65));

        // Example 1: Try with the specific ANBROS file
        String originalFilename = "ANBROS.xlsx";

        try {
            Map<String, List<Map<String, Object>>> result = convertExcelToJson(originalFilename, "anbros_data.json");

            if (result != null) {
                System.out.println("✅ Successfully converted Excel to JSON!");
                printSummary(result);
            } else {
                // Try with shorter filename
                System.out.println("\n📋 Trying with shorter filename...");
                result = convertExcelToJson("ANBROS.xlsx", "anbros_data.json");

                if (result == null) {
                    // Show available files
                    System.out.println("\n📋 Available Excel files:");
                    listAvailableExcelFiles();
                }
            }

        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }

        // Example usage instructions
        printUsageInstructions();
    }

    /**
     * Convert Excel file to JSON with automatic file finding
     */
    public static Map<String, List<Map<String, Object>>> convertExcelToJson(String filename, String outputFile) {
        try {
            // Find the Excel file
            Path filePath = findExcelFile(filename);

            if (filePath == null) {
                System.err.println("❌ Could not find Excel file: " + filename);
                return null;
            }

            System.out.println("📖 Reading Excel file: " + filePath);

            // Read and convert Excel file
            Map<String, List<Map<String, Object>>> allSheetsData = readExcelFile(filePath);

            // Save to JSON file if specified
            if (outputFile != null && !outputFile.trim().isEmpty()) {
                saveToJsonFile(allSheetsData, outputFile);
            }

            return allSheetsData;

        } catch (Exception e) {
            System.err.println("❌ Error processing Excel file: " + e.getMessage());
            return null;
        }
    }

    /**
     * Find Excel file in common Windows/IntelliJ locations
     */
    private static Path findExcelFile(String filename) {
        System.out.println("🔍 Searching for Excel file: " + filename);

        Path currentDir = Paths.get(System.getProperty("user.dir"));
        System.out.println("Current working directory: " + currentDir);

        // Search locations for Windows/IntelliJ
        List<Path> searchLocations = Arrays.asList(
                currentDir,                                          // Project root
                currentDir.resolve("src"),                           // src folder
                currentDir.resolve("src/main/resources"),            // Maven resources
                currentDir.resolve("data"),                          // data folder
                currentDir.resolve("files"),                         // files folder
                currentDir.resolve("assets"),                        // assets folder
                Paths.get(System.getProperty("user.home"), "Downloads"),  // Downloads
                Paths.get(System.getProperty("user.home"), "Desktop"),    // Desktop
                Paths.get(System.getProperty("user.home"), "Documents")   // Documents
        );

        // Add IntelliJ project root if we're in a subdirectory
        Path projectRoot = findIntellijProjectRoot(currentDir);
        if (projectRoot != null && !projectRoot.equals(currentDir)) {
            searchLocations.add(0, projectRoot);
        }

        System.out.println("\nSearching in the following locations:");

        for (Path location : searchLocations) {
            if (Files.exists(location)) {
                Path filePath = location.resolve(filename);
                System.out.println("  📁 " + location);
                System.out.println("    🔍 Checking: " + filePath);

                if (Files.exists(filePath)) {
                    System.out.println("    ✅ FOUND: " + filePath);
                    return filePath;
                } else {
                    System.out.println("    ❌ Not found");
                }
            } else {
                System.out.println("  📁 " + location + " (directory doesn't exist)");
            }
        }

        return null;
    }

    /**
     * Find IntelliJ project root by looking for .idea folder
     */
    private static Path findIntellijProjectRoot(Path startPath) {
        Path current = startPath;

        while (current != null && current.getParent() != null) {
            if (Files.exists(current.resolve(".idea"))) {
                return current;
            }
            current = current.getParent();
        }

        return null;
    }

    /**
     * Read Excel file and convert to Map structure
     */
    private static Map<String, List<Map<String, Object>>> readExcelFile(Path filePath) throws IOException {
        Map<String, List<Map<String, Object>>> allSheetsData = new LinkedHashMap<>();

        try (FileInputStream fis = new FileInputStream(filePath.toFile())) {
            Workbook workbook = createWorkbook(filePath, fis);

            // Process each sheet
            for (int i = 0; i < workbook.getNumberOfSheets(); i++) {
                Sheet sheet = workbook.getSheetAt(i);
                String sheetName = sheet.getSheetName();

                System.out.println("  📊 Processing sheet: " + sheetName);

                List<Map<String, Object>> sheetData = processSheet(sheet);
                allSheetsData.put(sheetName, sheetData);

                System.out.println("    ✅ " + sheetData.size() + " rows extracted");
            }

            workbook.close();
        }

        return allSheetsData;
    }

    /**
     * Create appropriate Workbook based on file extension
     */
    private static Workbook createWorkbook(Path filePath, FileInputStream fis) throws IOException {
        String fileName = filePath.getFileName().toString().toLowerCase();

        if (fileName.endsWith(".xlsx") || fileName.endsWith(".xlsm")) {
            return new XSSFWorkbook(fis);
        } else if (fileName.endsWith(".xls")) {
            return new HSSFWorkbook(fis);
        } else {
            throw new IllegalArgumentException("Unsupported file format: " + fileName);
        }
    }

    /**
     * Process individual Excel sheet
     */
    private static List<Map<String, Object>> processSheet(Sheet sheet) {
        List<Map<String, Object>> sheetData = new ArrayList<>();

        if (sheet.getPhysicalNumberOfRows() == 0) {
            return sheetData; // Empty sheet
        }

        // Get header row
        Row headerRow = sheet.getRow(sheet.getFirstRowNum());
        if (headerRow == null) {
            return sheetData;
        }

        // Extract headers
        List<String> headers = new ArrayList<>();
        for (Cell cell : headerRow) {
            headers.add(getCellValueAsString(cell));
        }

        // Process data rows
        for (int rowIndex = sheet.getFirstRowNum() + 1; rowIndex <= sheet.getLastRowNum(); rowIndex++) {
            Row row = sheet.getRow(rowIndex);

            if (row == null) {
                continue; // Skip empty rows
            }

            Map<String, Object> rowData = new LinkedHashMap<>();
            boolean hasData = false;

            // Process each cell in the row
            for (int cellIndex = 0; cellIndex < headers.size(); cellIndex++) {
                String header = headers.get(cellIndex);
                Object value = "";

                if (cellIndex < row.getLastCellNum()) {
                    Cell cell = row.getCell(cellIndex);
                    value = getCellValue(cell);
                }

                rowData.put(header, value);

                // Check if row has any data
                if (value != null && !value.toString().trim().isEmpty()) {
                    hasData = true;
                }
            }

            // Only add row if it has data
            if (hasData) {
                sheetData.add(rowData);
            }
        }

        return sheetData;
    }

    /**
     * Get cell value as appropriate Java object
     */
    private static Object getCellValue(Cell cell) {
        if (cell == null) {
            return "";
        }

        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getDateCellValue().toString();
                } else {
                    double numValue = cell.getNumericCellValue();
                    // Check if it's a whole number
                    if (numValue == Math.floor(numValue)) {
                        return (long) numValue;
                    } else {
                        return numValue;
                    }
                }
            case BOOLEAN:
                return cell.getBooleanCellValue();
            case FORMULA:
                try {
                    return cell.getStringCellValue();
                } catch (Exception e) {
                    try {
                        return cell.getNumericCellValue();
                    } catch (Exception e2) {
                        return cell.getCellFormula();
                    }
                }
            case BLANK:
            case _NONE:
            default:
                return "";
        }
    }

    /**
     * Get cell value as string (for headers)
     */
    private static String getCellValueAsString(Cell cell) {
        Object value = getCellValue(cell);
        return value != null ? value.toString() : "";
    }

    /**
     * Save data to JSON file
     */
    private static void saveToJsonFile(Map<String, List<Map<String, Object>>> data, String outputFile) {
        try {
            Path outputPath = Paths.get(outputFile);

            // If relative path, save in current directory
            if (!outputPath.isAbsolute()) {
                outputPath = Paths.get(System.getProperty("user.dir")).resolve(outputFile);
            }

            // Create directories if they don't exist
            Files.createDirectories(outputPath.getParent());

            // Write JSON file
            objectMapper.writeValue(outputPath.toFile(), data);

            System.out.println("\n💾 JSON data saved to: " + outputPath.toAbsolutePath());
            System.out.println("📂 You can find the file at: " + outputPath);

        } catch (IOException e) {
            System.err.println("❌ Error saving JSON file: " + e.getMessage());
        }
    }

    /**
     * Save individual sheets as separate JSON files
     */
    public static void saveIndividualSheets(String filename, String outputDir) {
        try {
            Path filePath = findExcelFile(filename);

            if (filePath == null) {
                System.err.println("❌ Could not find Excel file: " + filename);
                return;
            }

            Map<String, List<Map<String, Object>>> allSheetsData = readExcelFile(filePath);

            // Create output directory
            Path outputPath = Paths.get(System.getProperty("user.dir")).resolve(outputDir);
            Files.createDirectories(outputPath);
            System.out.println("📁 Output directory: " + outputPath);

            // Save each sheet
            for (Map.Entry<String, List<Map<String, Object>>> entry : allSheetsData.entrySet()) {
                String sheetName = entry.getKey();
                List<Map<String, Object>> sheetData = entry.getValue();

                if (!sheetData.isEmpty()) {
                    // Create Windows-safe filename
                    String safeSheetName = sheetName.replaceAll("[^a-zA-Z0-9\\s\\-_]", "").trim();
                    Path sheetFile = outputPath.resolve(safeSheetName + ".json");

                    objectMapper.writeValue(sheetFile.toFile(), sheetData);
                    System.out.println("💾 Saved " + sheetName + ": " + sheetData.size() + " records to " + sheetFile);
                }
            }

        } catch (Exception e) {
            System.err.println("❌ Error saving individual sheets: " + e.getMessage());
        }
    }

    /**
     * List available Excel files in common locations
     */
    private static void listAvailableExcelFiles() {
        List<String> excelExtensions = Arrays.asList(".xlsx", ".xls", ".xlsm", ".xlsb");

        Map<String, Path> searchDirs = new LinkedHashMap<>();
        searchDirs.put("Project Directory", Paths.get(System.getProperty("user.dir")));
        searchDirs.put("Downloads", Paths.get(System.getProperty("user.home"), "Downloads"));
        searchDirs.put("Desktop", Paths.get(System.getProperty("user.home"), "Desktop"));
        searchDirs.put("Documents", Paths.get(System.getProperty("user.home"), "Documents"));

        System.out.println("\n📋 Available Excel files:");

        for (Map.Entry<String, Path> entry : searchDirs.entrySet()) {
            String dirName = entry.getKey();
            Path dirPath = entry.getValue();

            if (Files.exists(dirPath)) {
                System.out.println("\n📁 " + dirName + " (" + dirPath + "):");

                try {
                    List<Path> excelFiles = Files.list(dirPath)
                            .filter(Files::isRegularFile)
                            .filter(path -> excelExtensions.stream()
                                    .anyMatch(ext -> path.getFileName().toString().toLowerCase().endsWith(ext)))
                            .collect(Collectors.toList());

                    if (excelFiles.isEmpty()) {
                        System.out.println("  (No Excel files found)");
                    } else {
                        for (Path file : excelFiles) {
                            System.out.println("  📄 " + file.getFileName());
                        }
                    }

                } catch (IOException e) {
                    System.out.println("  ❌ Permission denied");
                }
            }
        }
    }

    /**
     * Print summary of converted data
     */
    private static void printSummary(Map<String, List<Map<String, Object>>> data) {
        System.out.println("\n📊 Conversion Summary:");
        System.out.println("-".repeat(30));

        for (Map.Entry<String, List<Map<String, Object>>> entry : data.entrySet()) {
            String sheetName = entry.getKey();
            int recordCount = entry.getValue().size();
            System.out.println("📋 " + sheetName + ": " + recordCount + " records");
        }
    }

    /**
     * Print usage instructions
     */
    private static void printUsageInstructions() {
        System.out.println("\n📝 Usage Instructions for IntelliJ:");
        System.out.println("=".repeat(40));
        System.out.println("1. Place your Excel file in the project directory:");
        System.out.println("   📂 " + System.getProperty("user.dir"));
        System.out.println("2. Update the filename in your code");
        System.out.println("3. Run the program");

        System.out.println("\n💡 Example code usage:");
        System.out.println("   ExcelToJsonConverter.convertExcelToJson(\"your_file.xlsx\", \"output.json\");");
        System.out.println("   ExcelToJsonConverter.saveIndividualSheets(\"your_file.xlsx\", \"sheets_output\");");

        System.out.println("\n🔧 Debugging Information:");
        System.out.println("   Current directory: " + System.getProperty("user.dir"));
        System.out.println("   Java version: " + System.getProperty("java.version"));
        System.out.println("   User home: " + System.getProperty("user.home"));

        Path ideaDir = Paths.get(System.getProperty("user.dir"), ".idea");
        if (Files.exists(ideaDir)) {
            System.out.println("   ✅ Running in IntelliJ project");
        } else {
            System.out.println("   ⚠️  Not detected as IntelliJ project");
        }
    }

    /**
     * Quick convert method for easy use
     */
    public static Map<String, List<Map<String, Object>>> quickConvert(String filename) {
        String outputFile = filename.replaceFirst("\\.[^.]+$", "_converted.json");
        return convertExcelToJson(filename, outputFile);
    }

    /**
     * Convert to JSON string without saving to file
     */
    public static String convertToJsonString(String filename) {
        try {
            Map<String, List<Map<String, Object>>> data = convertExcelToJson(filename, null);
            if (data != null) {
                return objectMapper.writeValueAsString(data);
            }
        } catch (Exception e) {
            System.err.println("❌ Error converting to JSON string: " + e.getMessage());
        }
        return null;
    }
}