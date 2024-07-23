package com.service.util;
 
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import com.service.domain.AppConstant;
import com.service.domain.*;
import org.springframework.core.io.FileSystemResource;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.core.io.Resource;
import java.io.*;
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.ReadContext;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.Row;
import java.util.*;
import java.io.File;
import org.apache.commons.lang3.StringUtils;

public class FileUtil {

    public static String saveFile(String fileName, MultipartFile multipartFile, String filePathStr) throws IOException {
        Path uploadPath = Paths.get(filePathStr);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }
        //String fileCode = String.valueOf(jdId);
        try (InputStream inputStream = multipartFile.getInputStream()) {
            Path filePath = uploadPath.resolve(fileName);
            Files.copy(inputStream, filePath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException ioe) {
            throw new IOException("Could not save file: " + fileName, ioe);
        }
        return "";
    }

    public Resource getFile(MultipartFile file) throws Exception {
        File convFile = new File(file.getOriginalFilename());
        FileOutputStream fos = new FileOutputStream(convFile);
        fos.write(file.getBytes());
        fos.close();
        return new FileSystemResource(convFile);
    }

    public Integer getIntegerJsonValueFromString(String strMsg,String regExp) throws Exception {
        ReadContext ctx = JsonPath.parse(strMsg);
        Integer jobId = ctx.read(regExp);
        return jobId;
    }

    public String getStringJsonValueFromString(String strMsg,String regExp) throws Exception {
        ReadContext ctx = JsonPath.parse(strMsg);
        String str = ctx.read(regExp);
        return str;
    }

    public void writeToExcel(String jdId, String jdFilePath, String hiringManager,String jobTitle) throws Exception {
        XSSFWorkbook workbook = new XSSFWorkbook();
        XSSFSheet sheet =null;
        File file = new File(AppConstant.JD_DB_EXCEL_PATH);
        int rowNum = 0;
        Map<String, Object[]> data = new TreeMap<String, Object[]>();
        if (!file.exists()) {
            sheet = workbook.createSheet("JD Data");
            data.put("0", new Object[]{"JD_ID", "JOB_TITLE", "HIRING_MANAGER",  "JD_FILE_PATH"});
            rowNum =  0;
            Set<String> keyset = data.keySet();
            for (String key : keyset) {
                Row row = sheet.createRow(0);
                Object[] objArr = data.get(key);
                int cellnum = 0;
                for (Object obj : objArr) {
                    Cell cell = row.createCell(cellnum++);
                    if (obj instanceof String)
                        cell.setCellValue((String) obj);
                    else if (obj instanceof Integer)
                        cell.setCellValue((Integer) obj);
                }
            }
            data.clear();
        } else {
            FileInputStream myxls = new FileInputStream(AppConstant.JD_DB_EXCEL_PATH);
            workbook = new XSSFWorkbook(myxls);
            sheet = workbook.getSheetAt(0);
            rowNum =  sheet.getLastRowNum() ;
        }

        data.put(String.valueOf(rowNum +1), new Object[]{jdId, jobTitle, hiringManager,jdFilePath});

        Set<String> keyset = data.keySet();
        for (String key : keyset) {
            Row row = sheet.createRow(rowNum + 1);
            Object[] objArr = data.get(key);
            int cellnum = 0;
            for (Object obj : objArr) {
                Cell cell = row.createCell(cellnum++);
                if (obj instanceof String)
                    cell.setCellValue((String) obj);
                else if (obj instanceof Integer)
                    cell.setCellValue((Integer) obj);
            }
        }
        try {
            FileOutputStream out = new FileOutputStream(new File(AppConstant.JD_DB_EXCEL_PATH));
            workbook.write(out);
            out.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public List<JDDetail>  readJDExcel()  throws Exception{
        HashMap<Integer, Integer>  jdDetailsMap = new HashMap<Integer,Integer>();
        List<JDDetail> jdDetailList = new ArrayList<JDDetail>();
        FileInputStream file = new FileInputStream(new File(AppConstant.JD_DB_EXCEL_PATH));
        XSSFWorkbook workbook = new XSSFWorkbook(file);
        XSSFSheet sheet = workbook.getSheetAt(0);
        Iterator<Row> rowIterator = sheet.iterator();
        int rowCount =0;
        while(rowIterator.hasNext()) {
            Row row = rowIterator.next();
            if (rowCount > 0) {
                JDDetail jdDetail = new JDDetail();
                Iterator<Cell> cellIterator = row.cellIterator();
                int count = 0;
                while (cellIterator.hasNext()) {
                    Cell cell = cellIterator.next();
                    if (count == 0)
                        jdDetail.setId(cell.getStringCellValue());

                    if (count == 1)
                         jdDetail.setJobTitle(cell.getStringCellValue());

                    if (count == 2)
                        jdDetail.setHiringManager(cell.getStringCellValue());

                    if (count == 3)
                        jdDetail.setJdFilePath(cell.getStringCellValue());

                    count++;
                }
            jdDetailList.add(jdDetail);
          }
            rowCount++;
        }
        file.close();
        List<JDDetail> jdDetailListNew = new ArrayList<JDDetail>();
        for ( JDDetail jdDetl : jdDetailList){
            if (!jdDetailsMap.containsKey(Integer.valueOf(jdDetl.getId()))){
                jdDetailListNew.add(jdDetl);
                jdDetailsMap.put(Integer.valueOf(jdDetl.getId()), Integer.valueOf(jdDetl.getId()));
            }
        }
        return jdDetailListNew;
    }

    public List<TalentResult>  readTalentResultExcel()  throws Exception{
        List<TalentResult> talentResultList = new ArrayList<TalentResult>();
        FileInputStream file = new FileInputStream(new File(AppConstant.TALENT_MATCHING_RESULT_FILE_PATH));
        XSSFWorkbook workbook = new XSSFWorkbook(file);
        XSSFSheet sheet = workbook.getSheetAt(0);
        Iterator<Row> rowIterator = sheet.iterator();
        int rowCount =0;
        while(rowIterator.hasNext()) {
            Row row = rowIterator.next();
            if (rowCount > 0) {
                TalentResult talentResult = new TalentResult();
                Iterator<Cell> cellIterator = row.cellIterator();
                int count = 0;
                while (cellIterator.hasNext()) {
                    Cell cell = cellIterator.next();
                    if (count == 0) {
                        double value = cell.getNumericCellValue();
                        String formatted = StringUtils.removeEnd(String.valueOf(value), ".0");
                        talentResult.setSerialNum(formatted);
                    }

                    if (count == 1)
                        talentResult.setFirstName(cell.getStringCellValue());

                    if (count == 2)
                        talentResult.setLastName(cell.getStringCellValue());

                    if (count == 3)
                        talentResult.setDivision(cell.getStringCellValue());

                    if (count == 5)
                        talentResult.setLocation(cell.getStringCellValue());

                    if (count == 6)
                        talentResult.setCorporateTitle(cell.getStringCellValue());

                    if (count == 7)
                        talentResult.setCodeDescription(cell.getStringCellValue());

                    if (count == 17)
                        talentResult.setScore(cell.getNumericCellValue());

                    if (count == 18)
                        talentResult.setKsa(cell.getStringCellValue());

                    if (count == 19)
                        talentResult.setJobId(cell.getStringCellValue());

                    count++;
                }
                talentResultList.add(talentResult);
            }
            rowCount++;
        }
        file.close();
        return talentResultList;
    }

    public List<Employee>   readCandidateDetailsExcel()  throws Exception{
        List<Employee> employeeList = new ArrayList<Employee>();
        FileInputStream file = new FileInputStream(new File(AppConstant.CV_DETAILS_PATH));
        XSSFWorkbook workbook = new XSSFWorkbook(file);
        XSSFSheet sheet = workbook.getSheetAt(0);
        Iterator<Row> rowIterator = sheet.iterator();
        int rowCount =0;
        while(rowIterator.hasNext()) {
            Row row = rowIterator.next();
            if (rowCount > 0) {
                Employee employee = new Employee();
                Iterator<Cell> cellIterator = row.cellIterator();
                int count = 0;
                while (cellIterator.hasNext()) {
                    Cell cell = cellIterator.next();

                    if (count == 7)
                        employee.setEmployee_id(cell.getStringCellValue());

                    if (count == 8)
                        employee.setCvPath(cell.getStringCellValue());

                    count++;
                }
                employeeList.add(employee);
            }
            rowCount++;
        }
        file.close();
        return employeeList;
    }


    public  byte[] getFileContent(String folderPath) throws Exception {
        File folder = new File(AppConstant.CV_DETAILS_PATH);
        for (final File fileEntry : folder.listFiles()) {
            if (fileEntry.getName().startsWith(folderPath)) {
                FileInputStream resource = new FileInputStream(AppConstant.CV_DETAILS_PATH + "/" + fileEntry.getName());
                File file = new File(AppConstant.CV_DETAILS_PATH + "/" + fileEntry.getName());
                return Files.readAllBytes(file.toPath());
            }
        }
        return null;
    }

    public  byte[] getFileContentFromGivenPath(Employee employee, String filePath) throws Exception {
        filePath = filePath.replace("..","");
        filePath = AppConstant.CANDIDATE_CV_PATH + filePath;
        File file = new File(filePath);
        employee.setCvPath(filePath);
        return Files.readAllBytes(file.toPath());
        }
}
