package com.service.rest.impl;

import java.util.*;
import com.service.domain.Employee;
import com.service.business.EmployeeBO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import  com.service.domain.*;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.util.stream.Stream;

import org.springframework.core.io.Resource;

@RestController
@RequestMapping("/integrationservice")

public class IntegrationRestController {
    Logger logger  = LoggerFactory.getLogger(IntegrationRestController.class);

    @Autowired
    EmployeeBO employeeBO;


    @PostMapping(value="/jd-upload",  produces="application/json")
    public ResponseEntity<String> jdUpload(@RequestParam("file") MultipartFile multipartFile)  throws Exception {
        String response = this.employeeBO.jdUpload(multipartFile);
        return new ResponseEntity<>(response,HttpStatus.OK);
    }

    @PostMapping(value="/jd-submit",  consumes="application/json")
    public ResponseEntity<FileUploadResponse>  jdSubmit(@RequestBody  String jsonstr)  throws Exception {
        logger.info("Json payload for jdSubmit :   {} ",jsonstr);
        FileUploadResponse response = this.employeeBO.jdSubmit(jsonstr);
        return new ResponseEntity<>(response,HttpStatus.OK);
    }


    @GetMapping("/jd-list")
    public  @ResponseBody ResponseEntity<List<JDDetail>> jdList() throws Exception {
        List<JDDetail> list = this.employeeBO.jdList();
        return ResponseEntity.ok(list);
    }


    @GetMapping("/talent-results")
    public  @ResponseBody ResponseEntity<List<TalentResult>> talentResult(@RequestParam("job-id") String jdId)
            throws Exception {
        logger.info("Json payload for jdId :   {} ",jdId);
        List<TalentResult> list = this.employeeBO.talentResult(jdId);
        return ResponseEntity.ok(list);
    }


   /* @GetMapping("/candidate-info")
    public  @ResponseBody ResponseEntity<Employee>  candidtateInfo(@RequestParam("employee-id") String employeeId)
            throws Exception {
        logger.info("Json payload for employeeId :   {} ",employeeId);
        Employee employee = this.employeeBO.candidtateInfo(employeeId);
        return ResponseEntity.ok(employee);
    }*/

    @GetMapping("/candidate-info")
    public   ResponseEntity<?>  candidtateInfo(@RequestParam("employee-id") String employeeId) throws Exception {
        logger.info("Json payload for employeeId :   {} ",employeeId);
        Employee employee = this.employeeBO.candidtateInfo(employeeId);
        return ResponseEntity.status(HttpStatus.OK)
                .header("Content-Disposition","attachment; filename="+employee.getCvPath())
                .contentType(MediaType.valueOf("multipart/mixed"))
                .body(employee.getBytes());
    }
}
