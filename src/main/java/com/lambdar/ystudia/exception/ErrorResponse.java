package com.lambdar.ystudia.exception;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;


@Data
@AllArgsConstructor
public class ErrorResponse {

    private String message;

    private String description;

}
