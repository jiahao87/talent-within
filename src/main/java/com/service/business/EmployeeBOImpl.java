package com.service.business;

import com.service.domain.AppConstant;
import com.service.domain.FileUploadResponse;
import com.service.domain.JDDetail;
import com.service.util.FileUtil;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import java.util.ArrayList;
import java.util.List;
import com.service.domain.Employee;
import com.service.domain.TalentResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import java.io.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;


@Service
public class EmployeeBOImpl implements EmployeeBO {

    Logger logger  = LoggerFactory.getLogger(EmployeeBOImpl.class);

    public  String  jdUpload(MultipartFile multipartFile)  throws Exception  {
        String fileName = StringUtils.cleanPath(multipartFile.getOriginalFilename());
        String filePathStr = AppConstant.JD_SUBMIT_UPLOAD_PATH+"/"+fileName;
        String filecode = FileUtil.saveFile(fileName, multipartFile, AppConstant.JD_SUBMIT_UPLOAD_PATH);
        filePathStr = AppConstant.PYTHON_JD_READ_PATH+fileName;
        String payload =  "{\"filepath\" : \""+filePathStr+"\" }";
        String jsonResponse = callPythonEndpoint(payload, AppConstant.PYTHON_EXTRACT_JD_ENDPOINT_URL);
        return jsonResponse;
    }


    public  FileUploadResponse jdSubmit(String payload)  throws Exception  {
        String jsonResponse = callAsynchPythonEndpoint( payload, AppConstant.PYTHON_TALENT_MATCHING_ENDPOINT_URL);
        FileUtil fileUtil= new FileUtil();
        String jdId = fileUtil.getStringJsonValueFromString(payload,"$.job_id");
        String jobTitle = fileUtil.getStringJsonValueFromString(payload,"$.job_title");
        String hiringManager = fileUtil.getStringJsonValueFromString(payload,"$.hiring_manager");
        String filePath= fileUtil.getStringJsonValueFromString(payload,"$.filepath");
        fileUtil.writeToExcel(jdId, filePath,hiringManager,jobTitle);
        FileUploadResponse response = new FileUploadResponse();
        response.setFilePath(filePath);
        response.setMessage("JD Submitted successfully");
        return response;
    }


    public  List<JDDetail>  jdList()  throws Exception  {
        FileUtil fileUtil= new FileUtil();
        List<JDDetail> jdDetailList =  fileUtil.readJDExcel();
        return jdDetailList;
    }


    public  List<TalentResult> talentResult(String jdId)  throws Exception  {
        FileUtil fileUtil= new FileUtil();
        List<TalentResult> talentResultList =  fileUtil.readTalentResultExcel();
        List<TalentResult> talentResultFinalList = new ArrayList<TalentResult>();
        for (TalentResult talentResult : talentResultList ){
            if (talentResult.getJobId().equalsIgnoreCase(jdId)){
                talentResultFinalList.add(talentResult);
            }
        }
        return talentResultFinalList;
    }


    public  Employee candidtateInfo(String employeeId)  throws Exception  {
        File directory = new File("./");
        System.out.println("File Path : =============="+directory.getAbsolutePath());
        FileUtil fileUtil= new FileUtil();
        List<Employee> candidateList =  fileUtil.readCandidateDetailsExcel();
        for (Employee employee : candidateList ){
            if (employee.getEmployee_id().equalsIgnoreCase(employeeId)){
                byte[]  fileContent = fileUtil.getFileContentFromGivenPath(employee,employee.getCvPath());
                employee.setBytes(fileContent);
                return employee;
            }
        }
        return null;
    }

    public String callPythonEndpoint(String requestJson, String endpointUrl)  throws Exception {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<String> requestEntity = new HttpEntity<String>(requestJson,headers);
        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> response = restTemplate.postForEntity(endpointUrl, requestEntity, String.class);
        return response.getBody();
    }

    public String callAsynchPythonEndpoint(String requestJson, String endpointUrl)  throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(1);
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<String> requestEntity = new HttpEntity<String>(requestJson,headers);

        executor.submit(() -> {
            ResponseEntity<String> response = restTemplate.postForEntity(endpointUrl, requestEntity, String.class);
        });
        executor.shutdown();
        return "";
    }

}